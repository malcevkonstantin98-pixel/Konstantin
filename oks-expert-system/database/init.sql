-- OKS Expert System Database Initialization
-- PostgreSQL with PostGIS extension for geospatial data

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enum types for status and roles
CREATE TYPE object_status AS ENUM ('строится', 'сдан', 'на_гарантии', 'эксплуатация', 'аварийный');
CREATE TYPE user_role AS ENUM ('администратор', 'руководитель_проекта', 'инженер_окс', 'инженер_эксплуатации', 'подрядчик', 'аудит');
CREATE TYPE task_status AS ENUM ('новая', 'в_работе', 'на_согласовании', 'выполнена', 'просрочена');
CREATE TYPE defect_priority AS ENUM ('низкий', 'средний', 'высокий', 'критический');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Objects table with geospatial data
CREATE TABLE objects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NOT NULL,
    status object_status NOT NULL DEFAULT 'эксплуатация',
    object_type VARCHAR(100),
    contractor_id INTEGER REFERENCES users(id),
    responsible_id INTEGER REFERENCES users(id),
    completion_date DATE,
    warranty_until DATE,
    location GEOGRAPHY(POINT, 4326), -- WGS84 coordinates
    boundary GEOGRAPHY(POLYGON, 4326), -- Property boundary polygon
    area_sqm DECIMAL(10,2),
    floor_count INTEGER,
    build_year INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index on location
CREATE INDEX idx_objects_location ON objects USING GIST(location);
CREATE INDEX idx_objects_boundary ON objects USING GIST(boundary);

-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    object_id INTEGER REFERENCES objects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    doc_type VARCHAR(100) NOT NULL, -- проектная, исполнительная, паспорт, журнал
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    version INTEGER DEFAULT 1,
    uploaded_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Defects table
CREATE TABLE defects (
    id SERIAL PRIMARY KEY,
    object_id INTEGER REFERENCES objects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority defect_priority NOT NULL DEFAULT 'средний',
    status VARCHAR(50) DEFAULT 'открыт',
    location_point GEOGRAPHY(POINT, 4326),
    detected_by INTEGER REFERENCES users(id),
    assigned_to INTEGER REFERENCES users(id),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    photos JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_defects_location ON defects USING GIST(location_point);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    object_id INTEGER REFERENCES objects(id) ON DELETE CASCADE,
    defect_id INTEGER REFERENCES defects(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status task_status NOT NULL DEFAULT 'новая',
    priority VARCHAR(50) DEFAULT 'средний',
    assigned_to INTEGER REFERENCES users(id),
    created_by INTEGER REFERENCES users(id),
    due_date DATE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Field reports table
CREATE TABLE field_reports (
    id SERIAL PRIMARY KEY,
    object_id INTEGER REFERENCES objects(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id),
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location GEOGRAPHY(POINT, 4326),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    voice_note_path VARCHAR(500),
    photos JSONB DEFAULT '[]',
    videos JSONB DEFAULT '[]',
    qr_code VARCHAR(100),
    status VARCHAR(50) DEFAULT 'черновик',
    synced BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_field_reports_location ON field_reports USING GIST(location);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data for Moscow region
INSERT INTO users (email, password_hash, full_name, role, phone) VALUES
('admin@oks.ru', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'Администратор Системы', 'администратор', '+7 495 000-00-01'),
('pm@oks.ru', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'Петров Иван Сергеевич', 'руководитель_проекта', '+7 495 000-00-02'),
('engineer1@oks.ru', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'Сидоров Алексей Петрович', 'инженер_окс', '+7 495 000-00-03'),
('engineer2@oks.ru', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'Козлова Мария Ивановна', 'инженер_эксплуатации', '+7 495 000-00-04'),
('contractor@oks.ru', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'ООО "СтройМонтаж"', 'подрядчик', '+7 495 000-00-05');

-- Sample objects in Moscow and Moscow Oblast
INSERT INTO objects (name, address, status, object_type, contractor_id, responsible_id, completion_date, warranty_until, location, area_sqm, floor_count, build_year) VALUES
('ЖК "Северное Сияние"', 'г. Москва, ул. Академика Королёва, д. 15', 'эксплуатация', 'жилой комплекс', 5, 2, '2022-06-15', '2027-06-15', ST_GeogFromText('SRID=4326;POINT(37.6176 55.8261)'), 45000.50, 25, 2022),
('БЦ "Москва-Сити"', 'г. Москва, Пресненская наб., д. 12', 'на_гарантии', 'бизнес-центр', 5, 2, '2023-09-01', '2028-09-01', ST_GeogFromText('SRID=4326;POINT(37.5392 55.7495)'), 125000.00, 95, 2023),
('Торговый центр "Авиапарк"', 'г. Москва, Ходынский б-р, д. 4', 'эксплуатация', 'торговый центр', 5, 3, '2021-03-20', '2026-03-20', ST_GeogFromText('SRID=4326;POINT(37.5167 55.7833)'), 380000.00, 4, 2021),
('ЖК "Новая Третьяковка"', 'г. Москва, ул. Большая Ордынка, д. 21', 'строится', 'жилой комплекс', 5, 2, '2025-12-01', NULL, ST_GeogFromText('SRID=4326;POINT(37.6289 55.7414)'), 28000.00, 18, 2025),
('Спортивный комплекс в Химках', 'МО, г. Химки, ул. Спортивная, д. 10', 'сдан', 'спортивный объект', 5, 4, '2024-01-15', '2029-01-15', ST_GeogFromText('SRID=4326;POINT(37.4297 55.8947)'), 15000.00, 3, 2024),
('Школа №1500', 'г. Москва, ул. Профсоюзная, д. 85', 'эксплуатация', 'образование', 5, 3, '2020-09-01', '2025-09-01', ST_GeogFromText('SRID=4326;POINT(37.5667 55.6667)'), 8500.00, 4, 2020),
('Детский сад "Ромашка"', 'МО, г. Балашиха, мкр. Центральный, д. 15', 'на_гарантии', 'образование', 5, 4, '2023-08-01', '2028-08-01', ST_GeogFromText('SRID=4326;POINT(37.9500 55.8000)'), 3200.00, 2, 2023),
('Поликлиника №123', 'г. Москва, Ленинский пр-т, д. 45', 'аварийный', 'медицинское учреждение', 5, 2, '2015-05-01', '2020-05-01', ST_GeogFromText('SRID=4326;POINT(37.5833 55.7167)'), 12000.00, 6, 2015);

-- Sample defects
INSERT INTO defects (object_id, title, description, priority, status, location_point, detected_by, assigned_to) VALUES
(1, 'Протечка кровли на секции 3', 'Обнаружена протечка во время дождя, требуется ремонт гидроизоляции', 'высокий', 'открыт', ST_GeogFromText('SRID=4326;POINT(37.6180 55.8265)'), 3, 5),
(2, 'Неисправность системы вентиляции', 'Шум в вентиляционной шахте на 45 этаже', 'средний', 'открыт', ST_GeogFromText('SRID=4326;POINT(37.5395 55.7498)'), 4, 5),
(7, 'Трещина в фасаде', 'Вертикальная трещина длиной 2м на северном фасаде', 'критический', 'открыт', ST_GeogFromText('SRID=4326;POINT(37.9505 55.8005)'), 4, 5);

-- Sample tasks
INSERT INTO tasks (object_id, defect_id, title, description, status, priority, assigned_to, created_by, due_date) VALUES
(1, 1, 'Устранение протечки кровли', 'Замена гидроизоляционного покрытия на участке 15м²', 'в_работе', 'высокий', 5, 3, '2024-12-25'),
(2, 2, 'Диагностика вентиляции', 'Провести обследование системы вентиляции', 'новая', 'средний', 5, 4, '2024-12-30'),
(7, 3, 'Ремонт фасада', 'Расшивка и герметизация трещины', 'новая', 'критический', 5, 4, '2024-12-20');

-- Sample documents
INSERT INTO documents (object_id, name, doc_type, file_path, file_size, mime_type, uploaded_by) VALUES
(1, 'Проектная документация ЖК Северное Сияние', 'проектная', '/docs/object_1/project.pdf', 15728640, 'application/pdf', 2),
(1, 'Исполнительная схема фундамента', 'исполнительная', '/docs/object_1/foundation_scheme.dwg', 2097152, 'application/acad', 3),
(2, 'Паспорт лифтового оборудования', 'паспорт', '/docs/object_2/elevator_passport.pdf', 524288, 'application/pdf', 4);

-- Sample field reports
INSERT INTO field_reports (object_id, author_id, title, description, location, photos, status, synced) VALUES
(1, 3, 'Ежемесячный осмотр объекта', 'Проведён плановый осмотр, выявлена протечка', ST_GeogFromText('SRID=4326;POINT(37.6176 55.8261)'), '["photo1.jpg", "photo2.jpg"]', 'завершён', TRUE),
(2, 4, 'Проверка систем жизнеобеспечения', 'Проверены системы вентиляции и кондиционирования', ST_GeogFromText('SRID=4326;POINT(37.5392 55.7495)'), '["photo3.jpg"]', 'завершён', TRUE);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_objects_updated_at BEFORE UPDATE ON objects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO oks_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO oks_user;
