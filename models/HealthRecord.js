const mongoose = require('mongoose');

const healthRecordSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  testDate: {
    type: Date,
    required: true
  },
  testType: {
    type: String,
    required: true
  },
  parameters: [{
    name: {
      type: String,
      required: true
    },
    value: {
      type: Number,
      required: true
    },
    unit: String,
    referenceRange: {
      min: Number,
      max: Number
    },
    status: {
      type: String,
      enum: ['normal', 'low', 'high', 'critical'],
      required: true
    }
  }],
  originalFile: {
    filename: String,
    url: String,
    uploadDate: {
      type: Date,
      default: Date.now
    }
  },
  notes: String,
  provider: String,
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Update the updatedAt timestamp before saving
healthRecordSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('HealthRecord', healthRecordSchema);
