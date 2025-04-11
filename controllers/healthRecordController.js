const HealthRecord = require('../models/HealthRecord');
const AWS = require('aws-sdk');

// Configure AWS
const s3 = new AWS.S3({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
});

exports.createRecord = async (req, res) => {
  try {
    const { testDate, testType, parameters, provider, notes } = req.body;
    const file = req.file;

    let fileData = {};
    if (file) {
      // Upload file to S3
      const uploadResult = await s3.upload({
        Bucket: process.env.AWS_BUCKET_NAME,
        Key: `${req.user.id}/${Date.now()}-${file.originalname}`,
        Body: file.buffer,
        ContentType: file.mimetype,
        ACL: 'private'
      }).promise();

      fileData = {
        filename: file.originalname,
        url: uploadResult.Location,
        uploadDate: new Date()
      };
    }

    const healthRecord = new HealthRecord({
      user: req.user.id,
      testDate,
      testType,
      parameters,
      provider,
      notes,
      originalFile: fileData
    });

    await healthRecord.save();
    res.status(201).json(healthRecord);
  } catch (error) {
    res.status(500).json({ error: 'Error creating health record' });
  }
};

exports.getRecords = async (req, res) => {
  try {
    const records = await HealthRecord.find({ user: req.user.id })
      .sort({ testDate: -1 });
    res.json(records);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching health records' });
  }
};

exports.getRecord = async (req, res) => {
  try {
    const record = await HealthRecord.findOne({
      _id: req.params.id,
      user: req.user.id
    });

    if (!record) {
      return res.status(404).json({ error: 'Record not found' });
    }

    res.json(record);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching health record' });
  }
};

exports.updateRecord = async (req, res) => {
  try {
    const record = await HealthRecord.findOneAndUpdate(
      { _id: req.params.id, user: req.user.id },
      { $set: req.body },
      { new: true }
    );

    if (!record) {
      return res.status(404).json({ error: 'Record not found' });
    }

    res.json(record);
  } catch (error) {
    res.status(500).json({ error: 'Error updating health record' });
  }
};

exports.deleteRecord = async (req, res) => {
  try {
    const record = await HealthRecord.findOne({
      _id: req.params.id,
      user: req.user.id
    });

    if (!record) {
      return res.status(404).json({ error: 'Record not found' });
    }

    // Delete file from S3 if exists
    if (record.originalFile && record.originalFile.url) {
      const key = record.originalFile.url.split('.com/')[1];
      await s3.deleteObject({
        Bucket: process.env.AWS_BUCKET_NAME,
        Key: key
      }).promise();
    }

    await record.remove();
    res.json({ message: 'Record deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Error deleting health record' });
  }
};
