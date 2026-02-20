import express from 'express';
import { createClient } from 'redis';

const app = express();
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const client = createClient({ url: REDIS_URL });

client.on('error', (err) => console.error('Redis Connection Error:', err));

async function run() {
    await client.connect();
    console.log('Redis Connection Successful');

    await client.set('event_stock', 1000);

    app.get('/apply', async (req, res) => {
        const userId = req.query.userId as string;

        if (!userId) {
            return res.status(400).send('userId needed');
        }

        try {
            const isNewUser = await client.sAdd('applied_users', userId);

            if (isNewUser === 0) {
                return res.status(400).json({ status: 'fail', message: '이미 참여하셨습니다.' });
            }

            const remainStock = await client.decr('event_stock');

            if (remainStock < 0) {
                return res.status(429).json({ status: 'fail', message: '선착순 마감되었습니다.' });
            }

            console.log(`[성공] 유저: ${userId}, 남은 재고: ${remainStock}`);
            return res.json({
                status: 'success',
                message: '응모 성공!',
                rank: 1000 - remainStock
            });

        } catch (error) {
            console.error('에러 발생:', error);
            res.status(500).send('서버 에러');
        }
    });

    app.listen(3000, () => {
        console.log('서버가 3000번 포트에서 실행 중');
    });
}

run();