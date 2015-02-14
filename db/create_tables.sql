CREATE TABLE pull_request (
    id INTEGER NOT NULL,
    project VARCHAR(100) NOT NULL,
    url VARCHAR(140) NOT NULL,
    state VARCHAR(12) NOT NULL,
    title VARCHAR(120) NOT NULL,
    user_login VARCHAR(20) NOT NULL,
    body TEXT NOT NULL,
    created_at DATE NOT NULL,
    PRIMARY KEY(id)
);
CREATE TABLE pull_request_commit (
    pr_id INTEGER NOT NULL REFERENCES pull_request(id),
    ordinality INTEGER NOT NULL DEFAULT '0',
    sha VARCHAR(40) NOT NULL,
    to_merge boolean default FALSE,
    ready_to_test boolean default FALSE,
    merged boolean default FALSE,
    raised_pr_id INTEGER REFERENCES pull_request(id),
    PRIMARY KEY(pr_id, sha)
);