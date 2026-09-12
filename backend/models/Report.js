import mongoose from 'mongoose';

const reportSchema = new mongoose.Schema({
  original_filename: {
    type: String,
    required: true
  },
  prediction: {
    type: Number,
    required: true
  },
  confidence: {
    type: Number,
    required: true
  },
  output_pdf: {
    type: String,
    required: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

export default mongoose.model('Report', reportSchema);
