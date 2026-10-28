const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3030;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

const Reviews = require('./review');
const Dealerships = require('./dealership');
const Cars = require('./inventory');

const dataDir = path.join(__dirname, 'data');
const reviewsData = JSON.parse(fs.readFileSync(path.join(dataDir, 'reviews.json'), 'utf8'));
const dealershipsData = JSON.parse(fs.readFileSync(path.join(dataDir, 'dealerships.json'), 'utf8'));
const carsData = JSON.parse(fs.readFileSync(path.join(dataDir, 'car_records.json'), 'utf8'));

app.get('/', (req, res) => {
  res.send('Welcome to the Mongoose API');
});

app.get('/fetchReviews', async (req, res) => {
  try {
    res.json(await Reviews.find());
  } catch (error) {
    res.status(500).json({ error: 'Error fetching reviews' });
  }
});

app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    res.json(await Reviews.find({ dealership: Number(req.params.id) }));
  } catch (error) {
    res.status(500).json({ error: 'Error fetching reviews' });
  }
});

app.get('/fetchDealers', async (req, res) => {
  try {
    res.json(await Dealerships.find());
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});

app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const state = req.params.state;
    const dealers = state.toLowerCase() === 'all'
      ? await Dealerships.find()
      : await Dealerships.find({
          state: { $regex: `^${state}$`, $options: 'i' }
        });
    res.json(dealers);
  } catch (error) {
    res.status(500).json({ error: 'Error filtering dealerships' });
  }
});

app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const dealer = await Dealerships.findOne({ id: Number(req.params.id) });
    if (!dealer) {
      return res.status(404).json({ error: 'Dealership not found' });
    }
    res.json(dealer);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealership' });
  }
});

app.get('/fetchCars', async (req, res) => {
  try {
    res.json(await Cars.find());
  } catch (error) {
    res.status(500).json({ error: 'Error fetching cars' });
  }
});

app.post('/insert_review', async (req, res) => {
  try {
    const data = req.body;
    const latest = await Reviews.findOne().sort({ id: -1 });

    const review = new Reviews({
      id: latest ? latest.id + 1 : 1,
      name: data.name,
      dealership: Number(data.dealership),
      review: data.review,
      purchase: data.purchase === true || data.purchase === 'true',
      purchase_date: data.purchase_date,
      car_make: data.car_make,
      car_model: data.car_model,
      car_year: Number(data.car_year)
    });

    res.status(201).json(await review.save());
  } catch (error) {
    console.error('Review insertion failed:', error.message);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

async function start() {
  try {
    const mongoUrl = process.env.MONGO_URL ||
      'mongodb://127.0.0.1:27017/dealershipsDB';

    await mongoose.connect(mongoUrl);

    if (await Reviews.countDocuments() === 0) {
      await Reviews.insertMany(reviewsData.reviews);
    }

    if (await Dealerships.countDocuments() === 0) {
      await Dealerships.insertMany(dealershipsData.dealerships);
    }

    if (await Cars.countDocuments() === 0) {
      await Cars.insertMany(carsData.cars);
    }

    app.listen(port, '0.0.0.0', () => {
      console.log(`Database API running on port ${port}`);
    });
  } catch (error) {
    console.error('Database startup failed:', error.message);
    process.exit(1);
  }
}

start();
