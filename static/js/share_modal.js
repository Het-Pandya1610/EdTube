const shareOverlay = document.getElementById("shareOverlay");
const closeShareBtn = document.getElementById("closeShare");
const shareLink = document.getElementById("shareLink");

/* OPEN SHARE (works for dropdown & anywhere) */
document.addEventListener("DOMContentLoaded", () => {

    const shareOverlay = document.getElementById("shareOverlay");
    const closeShare = document.getElementById("closeShare");
    const shareLink = document.getElementById("shareLink");
    const copyBtn = document.getElementById("copyLinkBtn");

    // 🔥 ALL share buttons
    document.querySelectorAll(".openShare").forEach(btn => {
        btn.addEventListener("click", () => {

            const videoId = btn.dataset.videoId;

            // your watch URL format
            const url = `${window.location.origin}/video/watch/?v=${videoId}`;

            shareLink.value = url;

            shareOverlay.classList.add("active");
        });
    });

    closeShare.addEventListener("click", () => {
        shareOverlay.classList.remove("active");
    });

    copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(shareLink.value);
        copyBtn.innerText = "Copied!";
        setTimeout(() => copyBtn.innerText = "Copy Link", 1500);
    });

});


document.getElementById("copyLinkBtn").addEventListener("click", () => {
    shareLink.select();
    document.execCommand("copy");
});

function openShareWindow(url) {
    window.open(url, "_blank", "width=600,height=500");
}

document.getElementById("shareFacebook").onclick = () => {
    openShareWindow(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareLink.value)}`);
};

document.getElementById("shareLinkedIn").onclick = () => {
    openShareWindow(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareLink.value)}`);
};

document.getElementById("shareReddit").onclick = () => {
    openShareWindow(`https://www.reddit.com/submit?url=${encodeURIComponent(shareLink.value)}`);
};

document.getElementById("shareWhatsApp").onclick = () => {
    openShareWindow(`https://wa.me/?text=${encodeURIComponent(shareLink.value)}`);
};

document.getElementById("shareTelegram").onclick = () => {
    openShareWindow(`https://t.me/share/url?url=${encodeURIComponent(shareLink.value)}`);
};

document.getElementById("shareEmail").onclick = () => {
    window.location.href = `mailto:?subject=Watch this video&body=${encodeURIComponent(shareLink.value)}`;
};
