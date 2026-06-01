if (!window.__recognizePageBridgeLoaded) {
  window.__recognizePageBridgeLoaded = true;

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type !== "RECOGNIZE_PAGE_EVENT") {
      return;
    }

    window.postMessage({
      source: "recognize-extension",
      payload: msg.payload
    }, window.location.origin);

    sendResponse({ ok: true });
  });
}
