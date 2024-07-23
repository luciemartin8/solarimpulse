SELECT
    gc.user_id,
    gc.message,
    gc.created AS date_of_request,
    c.jobtitle,
    c.firstname,
    c.lastname,
    c.email,
    c.phone,
    c.type,
    c.company_id AS company_id,
    c.last_seen,
    c.created AS date_company_created_user_acc,
    cmp.about_us,
    cmp.member_date AS date_company_was_member,
    cmp.name AS company_name,
    msg_counts.repeated_message,
    user_msg_counts.total_user_message
FROM guideconnects gc
INNER JOIN contacts c ON gc.user_id = c.user_id
LEFT JOIN companies cmp ON c.company_id = cmp.id
LEFT JOIN (
    SELECT user_id, message, COUNT(*) AS repeated_message
    FROM guideconnects
    GROUP BY user_id, message
) msg_counts ON gc.user_id = msg_counts.user_id AND gc.message = msg_counts.message
LEFT JOIN (
    SELECT user_id, COUNT(*) AS total_user_message
    FROM guideconnects
    GROUP BY user_id
) user_msg_counts ON gc.user_id = user_msg_counts.user_id;