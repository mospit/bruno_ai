-- Bruno AI Database Schema Initialization
-- Version: 0.1.0-mvp

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    dietary_preferences JSONB DEFAULT '{}',
    budget_limit DECIMAL(10,2),
    household_size INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Pantry items
CREATE TABLE IF NOT EXISTS pantry_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    quantity DECIMAL(10,2),
    unit VARCHAR(50),
    expiry_date DATE,
    purchase_date DATE,
    barcode VARCHAR(100),
    nutrition_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Shopping lists
CREATE TABLE IF NOT EXISTS shopping_lists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    budget_limit DECIMAL(10,2),
    estimated_total DECIMAL(10,2),
    actual_total DECIMAL(10,2),
    store_preference VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Shopping list items
CREATE TABLE IF NOT EXISTS shopping_list_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shopping_list_id UUID NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    quantity DECIMAL(10,2),
    unit VARCHAR(50),
    estimated_price DECIMAL(10,2),
    actual_price DECIMAL(10,2),
    is_purchased BOOLEAN DEFAULT false,
    priority INTEGER DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Meals and recipes
CREATE TABLE IF NOT EXISTS meals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cuisine_type VARCHAR(100),
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    prep_time INTEGER, -- minutes
    cook_time INTEGER, -- minutes
    serving_size INTEGER,
    nutrition_info JSONB,
    instructions TEXT[],
    tags TEXT[],
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_public BOOLEAN DEFAULT true
);

-- Meal ingredients
CREATE TABLE IF NOT EXISTS meal_ingredients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meal_id UUID NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
    ingredient_name VARCHAR(255) NOT NULL,
    quantity DECIMAL(10,2),
    unit VARCHAR(50),
    is_optional BOOLEAN DEFAULT false,
    substitutes TEXT[]
);

-- User meal plans
CREATE TABLE IF NOT EXISTS user_meal_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    meal_id UUID NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
    planned_date DATE NOT NULL,
    meal_type VARCHAR(50), -- breakfast, lunch, dinner, snack
    status VARCHAR(50) DEFAULT 'planned', -- planned, completed, skipped
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat conversations
CREATE TABLE IF NOT EXISTS chat_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES chat_conversations(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences and settings
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, setting_key)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_pantry_items_user_id ON pantry_items(user_id);
CREATE INDEX IF NOT EXISTS idx_pantry_items_expiry ON pantry_items(expiry_date);
CREATE INDEX IF NOT EXISTS idx_shopping_lists_user_id ON shopping_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_shopping_list_items_list_id ON shopping_list_items(shopping_list_id);
CREATE INDEX IF NOT EXISTS idx_meals_cuisine_type ON meals(cuisine_type);
CREATE INDEX IF NOT EXISTS idx_meal_plans_user_date ON user_meal_plans(user_id, planned_date);
CREATE INDEX IF NOT EXISTS idx_chat_conversations_user ON chat_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation ON chat_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_user_settings_user_key ON user_settings(user_id, setting_key);

-- Update triggers for timestamp fields
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pantry_items_updated_at BEFORE UPDATE ON pantry_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_shopping_lists_updated_at BEFORE UPDATE ON shopping_lists FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chat_conversations_updated_at BEFORE UPDATE ON chat_conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for development
INSERT INTO meals (name, description, cuisine_type, difficulty_level, prep_time, cook_time, serving_size, instructions, tags) VALUES
('Spaghetti Carbonara', 'Classic Italian pasta dish with eggs, cheese, and pancetta', 'Italian', 2, 15, 20, 4, 
 ARRAY['Cook spaghetti according to package directions', 'Fry pancetta until crispy', 'Beat eggs with parmesan', 'Toss hot pasta with egg mixture', 'Serve immediately'], 
 ARRAY['pasta', 'quick', 'italian']),
('Chicken Stir Fry', 'Healthy and quick chicken stir fry with vegetables', 'Asian', 2, 20, 15, 3,
 ARRAY['Cut chicken into strips', 'Heat oil in wok', 'Cook chicken until done', 'Add vegetables and stir fry', 'Season with soy sauce'],
 ARRAY['healthy', 'quick', 'asian', 'low-carb']),
('Vegetable Soup', 'Hearty vegetable soup perfect for meal prep', 'American', 1, 15, 45, 6,
 ARRAY['Chop all vegetables', 'Heat oil in large pot', 'Sauté onions and garlic', 'Add remaining vegetables and broth', 'Simmer until tender'],
 ARRAY['vegetarian', 'healthy', 'meal-prep', 'budget-friendly']);

-- Sample meal ingredients
INSERT INTO meal_ingredients (meal_id, ingredient_name, quantity, unit) VALUES
((SELECT id FROM meals WHERE name = 'Spaghetti Carbonara'), 'Spaghetti', 400, 'g'),
((SELECT id FROM meals WHERE name = 'Spaghetti Carbonara'), 'Pancetta', 150, 'g'),
((SELECT id FROM meals WHERE name = 'Spaghetti Carbonara'), 'Eggs', 3, 'whole'),
((SELECT id FROM meals WHERE name = 'Spaghetti Carbonara'), 'Parmesan Cheese', 100, 'g'),
((SELECT id FROM meals WHERE name = 'Chicken Stir Fry'), 'Chicken Breast', 500, 'g'),
((SELECT id FROM meals WHERE name = 'Chicken Stir Fry'), 'Mixed Vegetables', 300, 'g'),
((SELECT id FROM meals WHERE name = 'Chicken Stir Fry'), 'Soy Sauce', 30, 'ml'),
((SELECT id FROM meals WHERE name = 'Vegetable Soup'), 'Mixed Vegetables', 800, 'g'),
((SELECT id FROM meals WHERE name = 'Vegetable Soup'), 'Vegetable Broth', 1.5, 'l');

COMMIT;
