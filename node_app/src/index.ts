import 'dotenv/config';
import express from 'express';
import { createClient } from 'redis';
import * as Sentry from '@sentry/node';

const app = express();

Sentry.init({
    dsn: process.env.SENTRY_DSN_NODE,
    tracesSampleRate: 1.0,
    debug: true
});

console.log("SENTRY DSN:", process.env.SENTRY_DSN_NODE);

app.use(express.json());
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const client = createClient({ url: REDIS_URL });

client.on('error', (err) => console.error('Redis Connection Error:', err));

async function run() {
    await client.connect();
    console.log('Redis Connection Successful');

    await client.set('event_stock', 1000);

    app.post('/apply', async (req, res, next) => {
        const { userId } = req.body

        if (!userId) {
            return res.status(400).json({ status: 'fail', message: 'userId가 필요합니다'})
        }

        try {
            const isNewUser = await client.sAdd('applied_users', String(userId));

            if (isNewUser === 0) {
                return res.status(400).json({ status: 'fail', message: '이미 참여하셨습니다' });
            }

            const remainStock = await client.decr('event_stock');

            if (remainStock < 0) {
                return res.status(429).json({ status: 'fail', message: '선착순 마감되었습니다' });
            }

            console.log(`[성공] 유저: ${userId}, 남은 재고: ${remainStock}`);
            return res.json({
                status: 'success',
                message: '응모 성공!',
                rank: 1000 - remainStock
            });

        } catch (error) {
            console.error('에러 발생:', error);
            next(error);
        }
    });

    app.get("/debug-sentry", (req, res) => {
        throw new Error("sentry error test");
    });

    Sentry.setupExpressErrorHandler(app);

    app.listen(3000, () => {
        console.log('서버가 3000번 포트에서 실행 중');
    });
}

run();