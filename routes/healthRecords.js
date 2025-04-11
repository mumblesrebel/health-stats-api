const express = require('express');
const router = express.Router();
const multer = require('multer');
const { protect } = require('../middleware/auth');
const {
  createRecord,
  getRecords,
  getRecord,
  updateRecord,
  deleteRecord
} = require('../controllers/healthRecordController');

// Configure multer for memory storage
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
  }
});

router.use(protect); // All routes require authentication

router.route('/')
  .post(upload.single('file'), createRecord)
  .get(getRecords);

router.route('/:id')
  .get(getRecord)
  .put(updateRecord)
  .delete(deleteRecord);

module.exports = router;
