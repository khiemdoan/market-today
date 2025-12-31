require('dotenv').config();

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
let TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID || process.argv[2];

if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.error('❌ Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required');
    process.exit(1);
}

TELEGRAM_CHAT_ID = String(TELEGRAM_CHAT_ID);

async function fetchInterestRates() {
    const res = await fetch('https://cafef.vn/du-lieu/ajax/ajaxlaisuatnganhang.ashx');
    const apiData = await res.json();
    
    if (!apiData?.Success || !Array.isArray(apiData.Data)) return [];
    
    return apiData.Data.map(bank => {
        const getRate = (deposit) => {
            const rate = bank.interestRates?.find(r => r.deposit === deposit);
            return rate?.value ?? 'N/A';
        };
        
        return {
            bank: bank.name,
            rates: {
                0: getRate(0), 1: getRate(1), 3: getRate(3), 6: getRate(6),
                9: getRate(9), 12: getRate(12), 18: getRate(18), 24: getRate(24)
            }
        };
    });
}

async function generateChartImage(interestRates) {
    const sortedRates = interestRates
        .map(item => ({
            ...item,
            rate12month: item.rates[12] !== 'N/A' ? parseFloat(item.rates[12]) : 0
        }))
        .sort((a, b) => b.rate12month - a.rate12month)
        .slice(0, 10);
    
    console.log('📊 Top 10 banks:');
    sortedRates.forEach((item, i) => console.log(`   ${i + 1}. ${item.bank}: ${item.rate12month}%`));
    
    const dateStr = new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
    
    const chartConfig = {
        type: 'bar',
        data: {
            labels: sortedRates.map(item => item.bank),
            datasets: [{
                label: 'Lãi suất 12 tháng (%)',
                data: sortedRates.map(item => item.rate12month),
                backgroundColor: 'rgba(25, 118, 210, 0.6)',
                borderColor: 'rgba(25, 118, 210, 1)',
                borderWidth: 1,
                barThickness: 40
            }]
        },
        options: {
            scales: {
                yAxes: [{ ticks: { beginAtZero: true }, scaleLabel: { display: true, labelString: 'Lãi suất (%)', fontSize: 14, fontStyle: 'bold' } }],
                xAxes: [{ scaleLabel: { display: true, labelString: 'Ngân hàng', fontSize: 14, fontStyle: 'bold' }, ticks: { maxRotation: 45, minRotation: 45 } }]
            },
            title: { display: true, text: `Top 10 lãi suất 12 tháng - ${dateStr}`, fontSize: 18, fontStyle: 'bold' },
            legend: { display: true, position: 'top' },
            plugins: {
                datalabels: {
                    anchor: 'end', align: 'top', color: '#1976d2',
                    font: { weight: 'bold', size: 18 },
                    formatter: (value) => value > 0 ? value + '%' : ''
                }
            }
        }
    };
    
    const params = new URLSearchParams({
        c: JSON.stringify(chartConfig),
        width: '1400',
        height: '600',
        backgroundColor: 'white',
        format: 'jpg'
    });
    
    const res = await fetch(`https://quickchart.io/chart?${params}`);
    return Buffer.from(await res.arrayBuffer());
}

async function sendChartToTelegram(chatId, imageBuffer) {
    const boundary = '----WebKitFormBoundary' + Math.random().toString(36).substring(2);
    const dateStr = new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
    const caption = `📊 Biểu đồ lãi suất tiết kiệm kỳ hạn 12 tháng - ${dateStr}\n\n💡 Dữ liệu cập nhật từ CafeF`;
    
    const body = Buffer.concat([
        Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n${chatId}\r\n--${boundary}\r\nContent-Disposition: form-data; name="photo"; filename="chart.jpg"\r\nContent-Type: image/jpeg\r\n\r\n`),
        imageBuffer,
        Buffer.from(`\r\n--${boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n${caption}\r\n--${boundary}--\r\n`)
    ]);
    
    const res = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendPhoto`, {
        method: 'POST',
        headers: { 'Content-Type': `multipart/form-data; boundary=${boundary}` },
        body
    });
    
    const data = await res.json();
    if (!data.ok) throw new Error(data.description || 'Telegram API error');
    console.log(`✅ Chart sent to Telegram: ${chatId}`);
}

async function main() {
    try {
        console.log('🚀 Starting...');
        const interestRates = await fetchInterestRates();
        console.log(`✅ Fetched ${interestRates.length} banks`);
        
        const chartImage = await generateChartImage(interestRates);
        console.log(`✅ Chart generated (${(chartImage.length / 1024).toFixed(2)} KB)`);
        
        await sendChartToTelegram(TELEGRAM_CHAT_ID, chartImage);
        console.log('🎉 Done!');
        process.exit(0);
    } catch (error) {
        console.error('💥 Failed!', error.message);
        process.exit(1);
    }
}

if (require.main === module) main();
