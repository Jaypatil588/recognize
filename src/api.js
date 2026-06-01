import neo4j from 'neo4j-driver'

const NEO4J_URI = import.meta.env.VITE_NEO4J_URI
const NEO4J_USER = import.meta.env.VITE_NEO4J_USER
const NEO4J_PASSWORD = import.meta.env.VITE_NEO4J_PASSWORD

if (!NEO4J_URI || !NEO4J_USER || !NEO4J_PASSWORD) {
  throw new Error('Missing VITE_NEO4J_URI, VITE_NEO4J_USER, or VITE_NEO4J_PASSWORD.')
}

const driver = neo4j.driver(
  NEO4J_URI,
  neo4j.auth.basic(NEO4J_USER, NEO4J_PASSWORD)
)

function toNumber(value) {
  return neo4j.isInt(value) ? value.toNumber() : Number(value ?? 0)
}

async function read(cypher, params = {}) {
  const session = driver.session({ defaultAccessMode: neo4j.session.READ })
  try {
    const result = await session.executeRead(tx => tx.run(cypher, params))
    return result.records
  } finally {
    await session.close()
  }
}

function unsupported(feature) {
  throw new Error(`${feature} requires a server runtime. This Vercel build reads hosted Neo4j directly and does not run backend/main.py.`)
}

async function graph() {
  const [entityRows, chunkRows, relRows, mentionRows] = await Promise.all([
    read(`
      MATCH (e:Entity)
      OPTIONAL MATCH (e)-[r:RELATES_TO]-()
      WITH e, count(r) AS degree
      RETURN e.id AS id, e.name AS label, e.type AS type,
             e.description AS preview, degree
      ORDER BY degree DESC
      LIMIT 500
    `),
    read(`
      MATCH (c:Chunk)
      OPTIONAL MATCH (c)-[r:MENTIONS]->(:Entity)
      WITH c, count(r) AS degree
      RETURN c.id AS id, substring(c.text, 0, 50) AS label,
             c.text AS preview, degree
      ORDER BY degree DESC
      LIMIT 500
    `),
    read(`
      MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity)
      RETURN a.id AS source, b.id AS target,
             r.relation AS relation,
             toFloat(r.weight) / 10.0 AS strength
      LIMIT 1200
    `),
    read(`
      MATCH (c:Chunk)-[:MENTIONS]->(e:Entity)
      RETURN c.id AS source, e.id AS target,
             'MENTIONS' AS relation,
             0.5 AS strength
      LIMIT 1200
    `),
  ])

  const entityNodes = entityRows.map(record => {
    const preview = record.get('preview') || record.get('label') || ''
    return {
      id: record.get('id'),
      label: record.get('label'),
      type: record.get('type') || 'CONCEPT',
      preview: preview.length > 150 ? `${preview.slice(0, 150)}...` : preview,
      chunk_index: 0,
      connections: toNumber(record.get('degree')),
    }
  })

  const chunkNodes = chunkRows.map(record => {
    const label = record.get('label') || 'Chunk'
    return {
      id: record.get('id'),
      label: `${label}...`,
      type: 'CHUNK',
      preview: record.get('preview') || '',
      chunk_index: 0,
      connections: toNumber(record.get('degree')),
    }
  })

  const links = [...relRows, ...mentionRows].map(record => {
    const strength = Number(record.get('strength') ?? 0.3)
    return {
      source: record.get('source'),
      target: record.get('target'),
      relation: record.get('relation'),
      strength: Math.min(1, Math.max(0.1, strength)),
    }
  })

  return { nodes: [...entityNodes, ...chunkNodes], links }
}

async function stats() {
  const records = await read(`
    MATCH (d:Document)
    WITH count(d) AS docs
    MATCH (e:Entity)
    WITH docs, count(e) AS entities
    MATCH (c:Chunk)
    WITH docs, entities, count(c) AS chunks
    MATCH (comm:Community)
    RETURN docs, entities, chunks, count(comm) AS communities
  `)
  const row = records[0]
  return {
    docs: toNumber(row.get('docs')),
    entities: toNumber(row.get('entities')),
    chunks: toNumber(row.get('chunks')),
    communities: toNumber(row.get('communities')),
  }
}

async function communities() {
  const records = await read(`
    MATCH (c:Community)
    RETURN c.id AS id, c.summary AS summary, c.size AS size
    ORDER BY c.size DESC
    LIMIT 50
  `)
  return records.map(record => ({
    id: record.get('id'),
    summary: record.get('summary') || '',
    size: toNumber(record.get('size')),
  }))
}

async function query(queryText, k = 8) {
  const q = queryText.trim().toLowerCase()
  if (!q) return { answer: 'Enter a graph search query.', sources: [], mode: 'local' }

  const records = await read(`
    MATCH (e:Entity)
    WHERE toLower(coalesce(e.name, '')) CONTAINS $q
       OR toLower(coalesce(e.description, '')) CONTAINS $q
       OR toLower(coalesce(e.type, '')) CONTAINS $q
    OPTIONAL MATCH (e)-[r:RELATES_TO]-(n:Entity)
    WITH e, collect(DISTINCT {
      relation: r.relation,
      name: n.name,
      description: n.description
    })[0..6] AS neighbours
    RETURN e.id AS id, e.name AS name, e.type AS type,
           e.description AS description, neighbours
    LIMIT $k
  `, { q, k: neo4j.int(k) })

  if (!records.length) {
    return { answer: `No Neo4j entities matched "${queryText}".`, sources: [], mode: 'local' }
  }

  const sources = records.map(record => ({
    id: record.get('id'),
    filename: record.get('name'),
    text: record.get('description') || '',
    type: record.get('type') || 'CONCEPT',
  }))

  const sections = records.map(record => {
    const name = record.get('name')
    const type = record.get('type') || 'CONCEPT'
    const description = record.get('description') || 'No description stored.'
    const neighbours = record.get('neighbours')
      .filter(n => n.name)
      .map(n => `  - ${n.relation || 'RELATES_TO'}: ${n.name}${n.description ? ` - ${n.description}` : ''}`)
      .join('\n')
    return `### ${name} (${type})\n${description}${neighbours ? `\n\nRelated:\n${neighbours}` : ''}`
  })

  return {
    answer: sections.join('\n\n'),
    sources,
    mode: 'local',
  }
}

async function queryGlobal(queryText) {
  const records = await read(`
    MATCH (c:Community)
    WHERE toLower(coalesce(c.summary, '')) CONTAINS $q
    RETURN c.id AS id, c.summary AS summary, c.size AS size
    ORDER BY c.size DESC
    LIMIT 8
  `, { q: queryText.trim().toLowerCase() })

  if (!records.length) {
    return { answer: `No community summaries matched "${queryText}".`, sources: [], mode: 'global' }
  }

  return {
    answer: records.map(record => {
      const size = toNumber(record.get('size'))
      return `### Community ${record.get('id')} (${size} nodes)\n${record.get('summary') || ''}`
    }).join('\n\n'),
    sources: [],
    mode: 'global',
  }
}

export const api = {
  stats,
  graph,
  communities,
  query,
  queryGlobal,
  upload: () => unsupported('Document upload and ingestion'),
  transcribe: () => unsupported('Audio transcription'),
  buildCommunities: () => unsupported('Community detection'),
  deleteDocument: () => unsupported('Document deletion'),
}
