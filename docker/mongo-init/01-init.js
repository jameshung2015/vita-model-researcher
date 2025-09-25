// Initialize application database and indexes
const dbName = process.env.DB_NAME || 'agents_kb';
const db = db.getSiblingDB(dbName);

// Collections
db.createCollection('sources_cache');
db.createCollection('taxonomy_versions');
db.createCollection('entity_change_log');
db.createCollection('models_idx');

// Indexes
db.sources_cache.createIndex({ url: 1 });
db.sources_cache.createIndex({ fingerprint: 1 }, { unique: true });
db.entity_change_log.createIndex({ entity_id: 1, ts: -1 });

print('Initialized DB and indexes for ' + dbName);

