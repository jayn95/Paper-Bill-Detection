<script>
const imageInput = document.getElementById('imageInput');
const detectBtn = document.getElementById('detectBtn');
const preview = document.getElementById('preview');
const results = document.getElementById('results');
const loading = document.getElementById('loading');
const coinCheckboxes = document.querySelectorAll('.coinCheckbox');

let selectedFile = null;

// ✅ Only these formats are allowed for detection
const ALLOWED_TYPES = ['image/jpeg', 'image/png'];

/* ----------------------------
   Enforce ONE coin selection
-----------------------------*/
coinCheckboxes.forEach(box => {
    box.addEventListener('change', () => {
        if (box.checked) {
            coinCheckboxes.forEach(b => {
                if (b !== box) b.checked = false;
            });
        }
    });
});

/* ----------------------------
   File selection
-----------------------------*/
imageInput.addEventListener('change', () => {
    selectedFile = imageInput.files[0];
    preview.innerHTML = '';
    results.innerHTML = '';
    detectBtn.disabled = true;

    if (!selectedFile) return;

    // ❌ NOT JPG / PNG → BLOCK DETECTION
    if (!ALLOWED_TYPES.includes(selectedFile.type)) {
        results.innerHTML = `
            <p style="color:red;">
                Unsupported image format.<br>
                Please upload a JPG or PNG file.
            </p>
        `;
        return;
    }

    // ✅ Preview only for valid images
    const reader = new FileReader();
    reader.onload = () => {
        preview.innerHTML = `<img src="${reader.result}" alt="Preview">`;
    };
    reader.readAsDataURL(selectedFile);

    detectBtn.disabled = false;
});

/* ----------------------------
   Detect & Compute
-----------------------------*/
detectBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    loading.style.display = 'block';
    detectBtn.disabled = true;
    results.innerHTML = '';

    // ✅ Selected coin
    const selectedCoin = Array.from(coinCheckboxes)
        .find(c => c.checked)?.value;

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (selectedCoin) formData.append('coins', selectedCoin);

    try {
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        loading.style.display = 'none';
        detectBtn.disabled = false;

        // ❌ Backend error
        if (!response.ok) {
            results.innerHTML = `
                <p style="color:red;">
                    ${data.error || 'Upload failed.'}
                </p>
            `;
            return;
        }

        if (data.message) {
            results.innerHTML = `<p>${data.message}</p>`;
            return;
        }

        let billsHtml = '<ul>';
        Object.entries(data.bills_detected).forEach(([bill, count]) => {
            billsHtml += `<li>₱${bill}: ${count}</li>`;
        });
        billsHtml += '</ul>';

        let coinsHtml = '<ul>';
        Object.entries(data.coin_change).forEach(([coin, count]) => {
            coinsHtml += `<li>₱${coin}: ${count}</li>`;
        });
        coinsHtml += '</ul>';

        results.innerHTML = `
            <h3>Total Amount: ₱${data.total_amount}</h3>
            <h4>Bills Detected</h4>
            ${billsHtml}
            <h4>Exact Coin Change</h4>
            ${coinsHtml}
        `;

    } catch (error) {
        loading.style.display = 'none';
        detectBtn.disabled = false;
        results.innerHTML = `
            <p style="color:red;">
                Error processing image.
            </p>
        `;
    }
});
</script>