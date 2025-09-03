// app-code/user-service/server.js
const express = require('express');
const { Pool } = require('pg');
const app = express();
const port = 8080;

const serviceVersion = process.env.VERSION || 'v1';

// Database connection pool
const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: 5432,
});

app.get('/users/:userId/credit', async (req, res) => {
    const userId = parseInt(req.params.userId, 10);
    console.log(`[${serviceVersion}] Checking credit for user: ${userId}`);

    try {
        const result = await pool.query('SELECT credit FROM users WHERE id = $1', [userId]);

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'User not found' });
        }

        const userCredit = result.rows[0].credit;
        const status = userCredit > 0 ? 'approved' : 'declined';

        res.json({
            userId: userId,
            status: status,
            remainingCredit: userCredit,
            version: serviceVersion === 'v2' ? 'v2-enhanced-db-check' : 'v1-standard-db-check'
        });

    } catch (err) {
        console.error('Database query error', err.stack);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.listen(port, () => {
    console.log(`User Service [${serviceVersion}] listening on port ${port}`);
});