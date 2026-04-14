-- =========================================
-- PROJECT: User Behavior & Fraud Analysis
-- SYSTEM: Code Redemption Platform
-- =========================================

-- =========================================
-- 1. SUCCESS & FAILURE RATE
-- =========================================
SELECT 
    COUNT(CASE WHEN is_success = 'True' THEN 1 END) * 100.0 / COUNT(*) AS success_rate,
    COUNT(CASE WHEN is_success = 'False' THEN 1 END) * 100.0 / COUNT(*) AS failure_rate
FROM attempts_data;

-- =========================================
-- 2. FAILURE REASON ANALYSIS
-- =========================================
SELECT 
    reason, 
    COUNT(*) AS failure_count
FROM attempts_data
WHERE is_success = 'False'
GROUP BY reason
ORDER BY failure_count DESC;

-- =========================================
-- 3. PEAK USAGE TIME
-- =========================================
SELECT 
    HOUR(attempt_time) AS hour, 
    COUNT(*) AS attempts
FROM attempts_data
GROUP BY hour
ORDER BY attempts DESC;

-- =========================================
-- 4. TOP ACTIVE USERS
-- =========================================
SELECT 
    user_id, 
    COUNT(*) AS total_attempts
FROM attempts_data
GROUP BY user_id
ORDER BY total_attempts DESC
LIMIT 10;

-- =========================================
-- 5. USERS WITH MOST FAILED ATTEMPTS
-- =========================================
SELECT 
    user_id, 
    COUNT(*) AS failed_attempts
FROM attempts_data
WHERE is_success = 'False'
GROUP BY user_id
ORDER BY failed_attempts DESC
LIMIT 10;

-- =========================================
-- 6. SUCCESS RATE PER USER
-- =========================================
SELECT 
    user_id,
    AVG(CASE WHEN is_success = 'True' THEN 1 ELSE 0 END) * 100 AS success_rate
FROM attempts_data
GROUP BY user_id
ORDER BY success_rate DESC;

-- =========================================
-- 7. FRAUD VS NORMAL USERS
-- =========================================
SELECT 
    CASE 
        WHEN f.user_id IS NOT NULL THEN 'Fraud'
        ELSE 'Normal'
    END AS user_type,
    COUNT(DISTINCT a.user_id) AS total_users
FROM attempts_data a
LEFT JOIN flagged_users f 
    ON a.user_id = f.user_id
GROUP BY user_type;

-- =========================================
-- 8. MOST ACTIVE FRAUD USERS
-- =========================================
SELECT 
    f.user_id,
    COUNT(*) AS attempts
FROM attempts_data a
JOIN flagged_users f 
    ON f.user_id = a.user_id
WHERE is_success = 'False'
GROUP BY f.user_id
ORDER BY attempts DESC
LIMIT 10;

-- =========================================
-- 9. FRAUD REASONS DISTRIBUTION
-- =========================================
SELECT 
    reason,
    COUNT(*) AS count
FROM flagged_users
GROUP BY reason
ORDER BY count DESC;

-- =========================================
-- 10. ACTIVE USERS VS TOTAL USERS
-- =========================================
SELECT 
    (SELECT COUNT(DISTINCT user_id) FROM attempts_data) AS active_users,
    (SELECT COUNT(*) FROM users) AS total_users;

-- =========================================
-- END OF ANALYSIS
-- =========================================
