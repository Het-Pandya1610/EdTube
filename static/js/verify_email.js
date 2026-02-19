document.addEventListener("DOMContentLoaded", () => {

    const inputs = document.querySelectorAll(".otp-box");
    const hiddenInput = document.getElementById("final-otp");

    inputs[0].focus(); // autofocus first box

    inputs.forEach((input, index) => {

        // allow numbers only
        input.addEventListener("input", (e) => {
            input.value = input.value.replace(/[^0-9]/g, "");

            if (input.value && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }

            updateOTP();
        });

        // backspace -> previous box
        input.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && !input.value && index > 0) {
                inputs[index - 1].focus();
            }
        });

        // paste full OTP
        input.addEventListener("paste", (e) => {
            e.preventDefault();
            const pasteData = e.clipboardData.getData("text").trim();

            if (/^\d{6}$/.test(pasteData)) {
                inputs.forEach((box, i) => {
                    box.value = pasteData[i];
                });
                updateOTP();
                inputs[5].focus();
            }
        });

    });

    function updateOTP() {
        hiddenInput.value = Array.from(inputs)
                                 .map(input => input.value)
                                 .join("");
    }

});
