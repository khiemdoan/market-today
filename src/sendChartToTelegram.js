const https = require('https');
const { URL } = require('url');
require('dotenv').config();

/**
 * Fetch interest rates, generate chart and send to Telegram
 * Usage: node sendChartToTelegram.js [chatId]
 */

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
let TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID || process.argv[2];

// Validate required environment variables
if (!TELEGRAM_BOT_TOKEN) {
    console.error('❌ Error: TELEGRAM_BOT_TOKEN is required in .env file');
    process.exit(1);
}

if (!TELEGRAM_CHAT_ID) {
    console.error('❌ Error: TELEGRAM_CHAT_ID is required in .env file or as command line argument');
    console.error('Usage: node sendChartToTelegram.js [chatId]');
    console.error('\n💡 Cách lấy Chat ID:');
    console.error('   1. Mở Telegram, tìm bot @userinfobot và nhắn /start');
    console.error('   2. Bot sẽ trả về Chat ID của bạn (ví dụ: 123456789)');
    console.error('   3. Copy số đó vào file .env hoặc truyền vào command line');
    console.error('\n⚠️  Lưu ý: Bạn phải nhắn tin với bot của mình trước (gửi /start)');
    process.exit(1);
}

TELEGRAM_CHAT_ID = String(TELEGRAM_CHAT_ID);

function httpsGet(url, options = {}) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const requestOptions = {
            hostname: urlObj.hostname,
            port: urlObj.port || 443,
            path: urlObj.pathname + urlObj.search,
            method: 'GET',
            headers: options.headers || {}
        };

        const req = https.request(requestOptions, (res) => {
            let data = [];
            
            res.on('data', (chunk) => {
                data.push(chunk);
            });
            
            res.on('end', () => {
                const buffer = Buffer.concat(data);
                if (options.responseType === 'arraybuffer') {
                    resolve({ status: res.statusCode, data: buffer, headers: res.headers });
                } else {
                    try {
                        const text = buffer.toString('utf8');
                        resolve({ status: res.statusCode, data: JSON.parse(text), headers: res.headers });
                    } catch (e) {
                        resolve({ status: res.statusCode, data: buffer, headers: res.headers });
                    }
                }
            });
        });
        
        req.on('error', (error) => {
            reject(error);
        });
        
        req.setTimeout(options.timeout || 30000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });
        
        req.end();
    });
}

function httpsPost(url, body, options = {}) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const requestOptions = {
            hostname: urlObj.hostname,
            port: urlObj.port || 443,
            path: urlObj.pathname + urlObj.search,
            method: 'POST',
            headers: {
                'Content-Length': Buffer.byteLength(body),
                ...options.headers
            }
        };

        const req = https.request(requestOptions, (res) => {
            let data = [];
            
            res.on('data', (chunk) => {
                data.push(chunk);
            });
            
            res.on('end', () => {
                const buffer = Buffer.concat(data);
                try {
                    const text = buffer.toString('utf8');
                    const jsonData = JSON.parse(text);
                    resolve({ status: res.statusCode, data: jsonData, headers: res.headers });
                } catch (e) {
                    resolve({ status: res.statusCode, data: buffer, headers: res.headers });
                }
            });
        });
        
        req.on('error', (error) => {
            reject(error);
        });
        
        req.setTimeout(options.timeout || 30000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });
        
        req.write(body);
        req.end();
    });
}

async function fetchInterestRates() {
    try {
        const url = 'https://cafef.vn/du-lieu/ajax/ajaxlaisuatnganhang.ashx';
        const response = await httpsGet(url);
        
        const apiData = response.data;
        const interestRates = [];
        
        if (apiData && apiData.Success && Array.isArray(apiData.Data)) {
            apiData.Data.forEach(bank => {
                const getRateByDeposit = (deposit) => {
                    const rate = bank.interestRates.find(r => r.deposit === deposit);
                    return rate && rate.value !== null ? rate.value : 'N/A';
                };
                
                interestRates.push({
                    bank: bank.name,
                    rates: {
                        '0month': getRateByDeposit(0),
                        '1month': getRateByDeposit(1),
                        '3month': getRateByDeposit(3),
                        '6month': getRateByDeposit(6),
                        '9month': getRateByDeposit(9),
                        '12month': getRateByDeposit(12),
                        '18month': getRateByDeposit(18),
                        '24month': getRateByDeposit(24)
                    }
                });
            });
        }
        
        return interestRates;
    } catch (error) {
        console.error('❌ Error fetching interest rates:', error.message);
        throw error;
    }
}

async function generateChartImage(interestRates) {
    try {
        const period = '12month';
        
        const sortedRates = interestRates
            .map(item => ({
                ...item,
                rate12month: item.rates[period] !== 'N/A' && item.rates[period] !== null 
                    ? parseFloat(item.rates[period]) 
                    : 0
            }))
            .sort((a, b) => b.rate12month - a.rate12month)
            .slice(0, 10);
        
        console.log('📊 Top 10 banks with highest 12-month rates:');
        sortedRates.forEach((item, index) => {
            console.log(`   ${index + 1}. ${item.bank}: ${item.rate12month}%`);
        });
        
        const labels = sortedRates.map(item => item.bank);
        const data = sortedRates.map(item => item.rate12month);
        
        const dateStr = new Date().toLocaleDateString('vi-VN', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric' 
        });
        
        const chartConfig = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Lãi suất 12 tháng (%)',
                    data: data,
                    backgroundColor: 'rgba(25, 118, 210, 0.6)',
                    borderColor: 'rgba(25, 118, 210, 1)',
                    borderWidth: 1,
                    barThickness: 40
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Lãi suất (%)',
                            fontSize: 14,
                            fontStyle: 'bold'
                        }
                    }],
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Ngân hàng',
                            fontSize: 14,
                            fontStyle: 'bold'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }]
                },
                title: {
                    display: true,
                    text: `Top 10 lãi suất 12 tháng - ${dateStr}`,
                    fontSize: 18,
                    fontStyle: 'bold'
                },
                legend: {
                    display: true,
                    position: 'top'
                },
                plugins: {
                    datalabels: {
                        anchor: 'end',
                        align: 'top',
                        color: '#1976d2',
                        font: {
                            weight: 'bold',
                            size: 18
                        },
                        formatter: (value) => {
                            return value > 0 ? value + '%' : '';
                        }
                    }
                }
            }
        };
        
        const params = {
            c: JSON.stringify(chartConfig),
            width: '1400',
            height: '600',
            backgroundColor: 'white',
            format: 'jpg'
        };
        
        const queryString = Object.keys(params)
            .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
            .join('&');
        
        const url = `https://quickchart.io/chart?${queryString}`;
        const response = await httpsGet(url, {
            responseType: 'arraybuffer',
            timeout: 30000
        });
        
        return response.data;
    } catch (error) {
        console.error('❌ Error generating chart:', error.message);
        throw error;
    }
}

async function sendChartToTelegram(chatId, imageBuffer) {
    try {
        const boundary = '----WebKitFormBoundary' + Math.random().toString(36).substring(2);
        const caption = '📊 Biểu đồ lãi suất tiết kiệm kỳ hạn 12 tháng\n\n💡 Dữ liệu cập nhật từ CafeF';
        
        let body = '';
        body += `--${boundary}\r\n`;
        body += `Content-Disposition: form-data; name="chat_id"\r\n\r\n`;
        body += `${chatId}\r\n`;
        body += `--${boundary}\r\n`;
        body += `Content-Disposition: form-data; name="photo"; filename="chart.jpg"\r\n`;
        body += `Content-Type: image/jpeg\r\n\r\n`;
        
        const bodyStart = Buffer.from(body, 'utf8');
        const bodyEnd = Buffer.from(`\r\n--${boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n${caption}\r\n--${boundary}\r\nContent-Disposition: form-data; name="parse_mode"\r\n\r\nMarkdown\r\n--${boundary}--\r\n`, 'utf8');
        const fullBody = Buffer.concat([bodyStart, imageBuffer, bodyEnd]);
        
        const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendPhoto`;
        const response = await httpsPost(url, fullBody, {
            headers: {
                'Content-Type': `multipart/form-data; boundary=${boundary}`
            },
            timeout: 30000
        });
        
        if (!response.data.ok) {
            throw new Error(response.data.description || 'Telegram API error');
        }
        
        console.log(`✅ Chart sent successfully to Telegram chat: ${chatId}`);
    } catch (error) {
        if (error.message && error.message.includes('chat not found')) {
            console.error('\n❌ Error: Chat not found!');
            console.error('\n💡 Cách khắc phục:');
            console.error('   1. Đảm bảo bạn đã nhắn tin với bot của mình trước (gửi /start)');
            console.error('   2. Kiểm tra lại TELEGRAM_CHAT_ID trong file .env');
            console.error('   3. Lấy Chat ID mới bằng cách nhắn với @userinfobot trên Telegram');
            console.error(`\n   Chat ID hiện tại: ${chatId}`);
        } else {
            console.error('❌ Error sending chart to Telegram:', error.message);
        }
        throw error;
    }
}

async function main() {
    try {
        console.log('🚀 Starting process...');
        
        // Step 1: Fetch interest rates
        console.log('🔄 Fetching interest rate data from CafeF...');
        const interestRates = await fetchInterestRates();
        console.log(`✅ Fetched data for ${interestRates.length} banks`);
        
        console.log('🎨 Generating chart...');
        const chartImage = await generateChartImage(interestRates);
        console.log(`✅ Chart generated (${(chartImage.length / 1024).toFixed(2)} KB)`);
        
        console.log(`📤 Sending chart to Telegram chat: ${TELEGRAM_CHAT_ID}...`);
        await sendChartToTelegram(TELEGRAM_CHAT_ID, chartImage);
        
        console.log('\n🎉 Done! Chart sent successfully to Telegram!');
        process.exit(0);
    } catch (error) {
        console.error('\n💥 Failed!', error.message);
        process.exit(1);
    }
}

// Run the script
if (require.main === module) {
    main();
}

