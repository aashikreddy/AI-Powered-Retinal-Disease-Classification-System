import express from 'express';
import multer from 'multer';
import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import mongoose from 'mongoose';
import Report from '../models/Report.js';
import { authenticateToken } from '../middleware/auth.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const router = express.Router();

const upload = multer({ 
  dest: 'uploads/',
  limits: {
    fileSize: 10 * 1024 * 1024
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new multer.MulterError('INVALID_FILE_TYPE'), false);
    }
  }
});

const uploadMiddleware = (req, res, next) => {
  upload.single('pdf')(req, res, (err) => {
    if (err instanceof multer.MulterError) {
      if (err.code === 'LIMIT_FILE_SIZE') {
        return res.status(400).json({ message: 'File too large. Maximum size is 10 MB.' });
      }
      if (err.code === 'INVALID_FILE_TYPE') {
        return res.status(400).json({ message: 'Invalid file type. Only PDF files are allowed.' });
      }
      return res.status(400).json({ message: `Upload error: ${err.message}` });
    } else if (err) {
      return res.status(400).json({ message: `Unknown upload error: ${err.message}` });
    }
    next();
  });
};

router.post('/upload', authenticateToken, uploadMiddleware, async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No PDF file uploaded' });
    }

    const formData = new FormData();
    formData.append('file', fs.createReadStream(req.file.path), {
      filename: req.file.originalname,
      contentType: 'application/pdf'
    });

    if (!process.env.INTERNAL_API_KEY) {
      return res.status(500).json({ message: 'Server configuration error: Missing internal API key' });
    }

    const headers = formData.getHeaders();
    headers['x-internal-secret'] = process.env.INTERNAL_API_KEY;

    const fastapiResponse = await axios.post(
      `${process.env.FASTAPI_URL}/infer_pdf`,
      formData,
      { headers }
    );

    const { prediction, confidence, output_pdf } = fastapiResponse.data;

    const report = new Report({
      original_filename: req.file.originalname,
      prediction,
      confidence,
      output_pdf,
      userId: req.user.userId
    });

    await report.save();

    fs.unlinkSync(req.file.path);

    res.json({
      message: 'Report processed successfully',
      report: {
        id: report._id,
        original_filename: report.original_filename,
        prediction: report.prediction,
        confidence: report.confidence,
        output_pdf: report.output_pdf,
        createdAt: report.createdAt
      }
    });
  } catch (error) {
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }

    console.error('Upload error:', error);
    
    if (error.response && error.response.status >= 400 && error.response.status < 500) {
      return res.status(error.response.status).json({
        message: 'Failed to process report',
        error: error.response.data
      });
    }

    res.status(500).json({
      message: 'Failed to process report',
      error: error.response?.data || error.message
    });
  }
});

router.get('/history', authenticateToken, async (req, res) => {
  try {
    const reports = await Report.find({ userId: req.user.userId }).sort({ createdAt: -1 });
    res.json({ reports });
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch reports', error: error.message });
  }
});

router.get('/download/:id', authenticateToken, async (req, res) => {
  try {
    if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
      return res.status(400).json({ message: 'Invalid report ID format' });
    }

    const report = await Report.findOne({ _id: req.params.id, userId: req.user.userId });

    if (!report) {
      return res.status(404).json({ message: 'Report not found or unauthorized' });
    }

    console.log('Report found:', report._id);
    console.log('Stored output_pdf:', report.output_pdf);

    // Build path to PDF file - go up one level from routes to backend directory
    const pdfDir = path.join(__dirname, '..', 'ai_diagnostic_reports');
    
    // Handle both old format (full path) and new format (just filename)
    let pdfFilename = report.output_pdf;
    if (report.output_pdf.includes('ai_diagnostic_reports')) {
      // Old format: extract just the filename
      pdfFilename = path.basename(report.output_pdf);
    }
    
    const filePath = path.join(pdfDir, pdfFilename);
    
    console.log('PDF directory:', pdfDir);
    console.log('PDF filename:', pdfFilename);
    console.log('Full file path:', filePath);
    console.log('File exists:', fs.existsSync(filePath));

    if (!fs.existsSync(filePath)) {
      console.error('PDF file not found');
      // List what files exist in the directory
      try {
        const filesInDir = fs.readdirSync(pdfDir);
        console.log('Files in ai_diagnostic_reports:', filesInDir);
      } catch (e) {
        console.log('Could not read directory:', e.message);
      }
      return res.status(404).json({ 
        message: 'PDF file not found on server', 
        requestedFile: pdfFilename,
        lookingIn: filePath
      });
    }

    res.download(filePath, `AI_Report_${report._id}.pdf`);
  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({ message: 'Failed to download report', error: error.message });
  }
});

export default router;
