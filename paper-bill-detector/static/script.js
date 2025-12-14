const imageInput = document.getElementById('imageInput');
const detectBtn = document.getElementById('detectBtn');
const preview = document.getElementById('preview');
const results = document.getElementById('results');
const loading = document.getElementById('loading');

let selectedFile = null;

imageInput.addEventListener('change', () => {
    selectedFile = imageInput.files[0];
    results.innerHTML = '';

    if (!selectedFile) {
        detectBtn.disabled = true;
        preview.innerHTML = '';
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        preview.innerHTML = `<img src="${reader.result}" alt="Image preview">`;
    };
    reader.readAsDataURL(selectedFile);

    detectBtn.disabled = false;
});

detectBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    loading.style.display = 'block';
    detectBtn.disabled = true;
    results.innerHTML = '';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        loading.style.display = 'none';
        detectBtn.disabled = false;

        if (data.message) {
            results.innerHTML = `<p>${data.message}</p>`;
            return;
        }

        let billsHtml = '<ul>';
        for (const bill in data.bills_detected) {
            billsHtml += `<li>₱${bill}: ${data.bills_detected[bill]}</li>`;
        }
        billsHtml += '</ul>';

        let coinsHtml = '<ul>';
        for (const coin in data.coin_change) {
            coinsHtml += `<li>₱${coin}: ${data.coin_change[coin]}</li>`;
        }
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
        results.innerHTML = '<p>Failed to process image.</p>';
    }
});
