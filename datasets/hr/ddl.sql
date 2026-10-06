-- =====================================================================
-- Dataset: hr   Version: v1
-- Used by: Chapter 49 (HR and Workforce Analytics)
-- Size: ~1,200 employees. Workforce data is small by nature; nothing in
--       this project needs volume, and small outputs are printable.
-- The schema name is supplied by psql: -v schema=hr
--
-- NO PROTECTED ATTRIBUTES. There is no race, ethnicity, gender, age, date
-- of birth, religion, disability, marital status or health column anywhere
-- in this schema, and no analysis in the chapter derives one. Workforce
-- analytics that segments people on those attributes is a legal and ethical
-- matter rather than a SQL one, and a SQL book is the wrong place to teach
-- it by example. Everything here cuts by department, job family, job level,
-- location, tenure and performance -- which is what the operational
-- questions actually need.
-- =====================================================================

DROP SCHEMA IF EXISTS :schema CASCADE;
CREATE SCHEMA :schema;
SET search_path TO :schema;

CREATE TABLE departments (
    dept_id         integer PRIMARY KEY,
    dept_name       text        NOT NULL,
    cost_centre     text        NOT NULL,
    parent_dept_id  integer     REFERENCES departments(dept_id),
    location        text        NOT NULL
);

CREATE TABLE salary_bands (
    pay_grade       text PRIMARY KEY,
    job_level       smallint    NOT NULL,
    band_min        numeric(10,2) NOT NULL,
    band_mid        numeric(10,2) NOT NULL,       -- the compa-ratio denominator
    band_max        numeric(10,2) NOT NULL,
    CHECK (band_min <= band_mid AND band_mid <= band_max)
);

CREATE TABLE employees (
    employee_id     integer PRIMARY KEY,
    first_name      text        NOT NULL,
    last_name       text        NOT NULL,
    work_email      text,                         -- deliberately nullable
    dept_id         integer     NOT NULL REFERENCES departments(dept_id),
    manager_id      integer     REFERENCES employees(employee_id),
    job_family      text        NOT NULL,
    job_level       smallint    NOT NULL,
    employment_type text        NOT NULL,         -- full_time | part_time | contract
    fte             numeric(3,2) NOT NULL,        -- headcount vs FTE differ because of this
    hire_date       date        NOT NULL,
    termination_date date,                        -- NULL = currently employed
    leaver_type     text,                         -- voluntary | involuntary | NULL
    location        text        NOT NULL,
    CHECK (termination_date IS NULL OR termination_date >= hire_date),
    CHECK ((termination_date IS NULL) = (leaver_type IS NULL))
);

-- Type 2 compensation history: one row per salary a person has held.
CREATE TABLE compensation (
    employee_id     integer     NOT NULL REFERENCES employees(employee_id),
    valid_from      date        NOT NULL,
    valid_to        date,                         -- NULL = current row
    base_salary     numeric(10,2) NOT NULL,
    pay_grade       text        NOT NULL REFERENCES salary_bands(pay_grade),
    change_reason   text        NOT NULL,         -- hire | merit | promotion | adjustment
    PRIMARY KEY (employee_id, valid_from),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
);

CREATE TABLE performance_reviews (
    review_id       integer PRIMARY KEY,
    employee_id     integer     NOT NULL REFERENCES employees(employee_id),
    review_year     smallint    NOT NULL,
    rating          smallint    NOT NULL CHECK (rating BETWEEN 1 AND 5),
    reviewer_id     integer     REFERENCES employees(employee_id),
    UNIQUE (employee_id, review_year)
);

CREATE TABLE requisitions (
    req_id          integer PRIMARY KEY,
    dept_id         integer     NOT NULL REFERENCES departments(dept_id),
    job_family      text        NOT NULL,
    job_level       smallint    NOT NULL,
    opened_date     date        NOT NULL,
    closed_date     date,                         -- NULL = still open
    outcome         text                          -- filled | cancelled | NULL
);

CREATE TABLE applications (
    application_id  integer PRIMARY KEY,
    req_id          integer     NOT NULL REFERENCES requisitions(req_id),
    applied_date    date        NOT NULL,
    stage           text        NOT NULL,         -- furthest stage reached
    stage_date      date        NOT NULL,
    hired_employee_id integer   REFERENCES employees(employee_id)
);

CREATE TABLE absences (
    employee_id     integer     NOT NULL REFERENCES employees(employee_id),
    absence_date    date        NOT NULL,
    hours           numeric(4,2) NOT NULL,
    category        text        NOT NULL,         -- annual_leave | sick | other
    PRIMARY KEY (employee_id, absence_date)
);

-- The grain of each table, recorded where it cannot drift away from the
-- schema. Example 917 reads these back out of the catalog: a grain written
-- in a wiki is a grain that is wrong within a quarter.
COMMENT ON TABLE departments         IS 'one row per department';
COMMENT ON TABLE salary_bands        IS 'one row per pay grade';
COMMENT ON TABLE employees           IS 'one row per person, ever employed';
COMMENT ON TABLE compensation        IS 'one row per person per salary held (type 2)';
COMMENT ON TABLE performance_reviews IS 'one row per person per review year';
COMMENT ON TABLE requisitions        IS 'one row per open position';
COMMENT ON TABLE applications        IS 'one row per candidate per requisition';
COMMENT ON TABLE absences            IS 'one row per person per absent day';
