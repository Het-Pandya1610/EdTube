document.addEventListener("DOMContentLoaded", () => {
    const tabUrl = document.getElementById("tabUrl");
    const tabMedia = document.getElementById("tabMedia");
    const videoByUrl = document.getElementById("videoByUrl");
    const videoByMedia = document.getElementById("videoByMedia");

    const videoUrlInput = document.querySelector('input[name="video_url"]');
    const videoFileInput = document.querySelector('input[name="video_file"]');
    const thumbnailInput = document.querySelector('input[name="thumbnail"]');
    const languageUrl = document.getElementById('langUrl')
    const subjectUrl = document.getElementById('subUrl')
    const titleUrl = document.getElementById('titleUrl')
    const desUrl = document.getElementById('desUrl')
    const languageMedia = document.getElementById('langMedia')
    const subjectMedia = document.getElementById('subMedia')
    const titleMedia = document.getElementById('titleMedia')
    const desMed = document.getElementById('desMedia')

    window.addEventListener('DOMContentLoaded', () => {
        titleMedia.disabled = true;
        languageMedia.disabled = true;
        subjectMedia.disabled = true;
        desMed.disabled = true;

        titleUrl.disabled = false;
        languageUrl.disabled = false;
        subjectUrl.disabled = false;
        desUrl.disabled = false;
    });

    // DEFAULT STATE (Video by URL)
    videoUrlInput.required = true;
    titleUrl.required = true;
    languageUrl.required = true;
    subjectUrl.required = true;
    if (videoFileInput) videoFileInput.required = false;
    if (thumbnailInput) thumbnailInput.required = false;
    if (titleMedia) titleMedia.required = false;
    if (languageMedia) languageMedia.required = false;
    if (subjectMedia) subjectMedia.required = false;


    tabUrl.addEventListener("click", () => {
        tabUrl.classList.add("active");
        tabMedia.classList.remove("active");

        videoByUrl.classList.add("active");
        videoByMedia.classList.remove("active");

        // REQUIRED TOGGLES
        videoUrlInput.required = true;
        titleUrl.required = true;
        languageUrl.required = true;
        subjectUrl.required = true;
        if (videoFileInput) videoFileInput.required = false;
        if (thumbnailInput) thumbnailInput.required = false;
        if (titleMedia) titleMedia.required = false;
        if (languageMedia) languageMedia.required = false;
        if (subjectMedia) subjectMedia.required = false;


        titleUrl.disabled = false;
        languageUrl.disabled = false;
        subjectUrl.disabled = false;
        desUrl.disabled = false;
        titleMedia.disabled = true;
        languageMedia.disabled = true;
        subjectMedia.disabled = true;
        desMed.disabled = true
    });

    tabMedia.addEventListener("click", () => {
        tabMedia.classList.add("active");
        tabUrl.classList.remove("active");

        videoByMedia.classList.add("active");
        videoByUrl.classList.remove("active");

        // REQUIRED TOGGLES
        videoUrlInput.required = false;
        titleUrl.required = false;
        languageUrl.required = false;
        subjectUrl.required = false;
        if (videoFileInput) videoFileInput.required = true;
        if (thumbnailInput) thumbnailInput.required = true;
        if (titleMedia) titleMedia.required = true;
        if (languageMedia) languageMedia.required = true;
        if (subjectMedia) subjectMedia.required = true;


        titleUrl.disabled = true;
        languageUrl.disabled = true;
        subjectUrl.disabled = true;
        desUrl.disabled = true;
        titleMedia.disabled = false;
        languageMedia.disabled = false;
        subjectMedia.disabled = false;
        desMed.disabled = false;
    });
    const uploadForm = document.querySelector("form");

    uploadForm.addEventListener("submit", function () {
      pageLoader.show({
          message: "Uploading video...",
          submessage: "Please wait while we process your content",
          type: "upload"
      });
    });
});

document.addEventListener("DOMContentLoaded", () => {
  const pasteBtn = document.getElementById("pasteBtn");
  const clearBtn = document.querySelector(".clear-btn");

  pasteBtn.addEventListener("click", pasteFromClipboard);
  clearBtn.addEventListener("click", clearVideoInput);
});


// Clipboard helpers (NO inline handlers)
async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    document.getElementById("videoUrlInput").value = text;
  } catch {
    alert("Clipboard access denied");
  }
}

function clearVideoInput() {
  const input = document.getElementById("videoUrlInput");
  input.value = "";
  input.focus();
}
