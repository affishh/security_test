const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const port = 4000;

app.use(bodyParser.urlencoded({ extended: true }));

// Vulnerable login endpoint
app.post('/login', (req, res) => {
    const { username, password } = req.body;

    // Intentional vulnerability: hardcoded credentials
    if (username === 'admin' && password === 'admin123') {
        res.send('Logged in successfully!');
    } else {
        res.send('Login failed.');
    }
});

app.get('/', (req, res) => {
    res.send(`
        <form method="post" action="/login">
            <input name="username" />
            <input name="password" type="password" />
            <button type="submit">Login</button>
        </form>
    `);
});

app.listen(port, () => {
    console.log(`Vulnerable app listening at http://localhost:${port}`);
});
