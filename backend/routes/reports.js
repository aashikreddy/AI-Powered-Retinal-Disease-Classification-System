import express from 'express';
import multer from 'multer';
import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import Report from '../models/Report.js';
import { authenticateToken } from '../middleware/auth.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const router = express.Router();

const upload = multer({ dest: 'uploads/' });

router.post('/upload', authenticateToken, upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No PDF file uploaded' });
    }

    const formData = new FormData();
    formData.append('file', fs.createReadStream(req.file.path), {
      filename: req.file.originalname,
      contentType: 'application/pdf'
    });

    const fastapiResponse = await axios.post(
      `${process.env.FASTAPI_URL}/infer_pdf`,
      formData,
      {
        headers: formData.getHeaders()
      }
    );

    const { prediction, confidence, output_pdf } = fastapiResponse.data;

    const report = new Report({
      original_filename: req.file.originalname,
      prediction,
      confidence,
      output_pdf
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
    res.status(500).json({
      message: 'Failed to process report',
      error: error.response?.data || error.message
    });
  }
});

router.get('/history', authenticateToken, async (req, res) => {
  try {
    const reports = await Report.find().sort({ createdAt: -1 });
    res.json({ reports });
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch reports', error: error.message });
  }
});

router.get('/download/:id', authenticateToken, async (req, res) => {
  try {
    const report = await Report.findById(req.params.id);

    if (!report) {
      return res.status(404).json({ message: 'Report not found in database' });
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
