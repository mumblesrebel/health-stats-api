require('dotenv').config();
const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const { Pool } = require('pg');

const authRoutes = require('./routes/auth');
const healthRecordRoutes = require('./routes/healthRecords');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Database connections
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => {
  console.log('Connected to MongoDB');
}).catch(err => {
  console.error('MongoDB connection error:', err);
});

const pgPool = new Pool({
  connectionString: process.env.POSTGRES_URI
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/health-records', healthRecordRoutes);

// Basic route
app.get('/', (req, res) => {
  res.json({ message: 'Health Stats Tracker API' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
