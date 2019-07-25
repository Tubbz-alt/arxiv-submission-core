-- Exports submissions and primary category from classic db.
-- For use with process_submissions.py
--
-- mysql -u root -B arXiv < export_submissions.sql > submissions.tsv
SELECT sub.*, cat.category, cat.is_primary
FROM arXiv.arXiv_submissions sub, arXiv.arXiv_submission_category cat
WHERE sub.submission_id = cat.submission_id
ORDER BY sub.submission_id DESC
LIMIT 1000;
