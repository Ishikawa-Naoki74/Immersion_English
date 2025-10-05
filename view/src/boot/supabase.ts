import { boot } from 'quasar/wrappers'
import { createClient } from '@supabase/supabase-js'
import { SUPABASE_CONFIG, validateSupabaseConfig } from 'src/utils/supabaseConfig'

// Validate configuration first
const configValidation = validateSupabaseConfig()
if (!configValidation.isValid) {
  console.error('❌ Supabase configuration errors:', configValidation.errors)
}

const supabaseUrl = SUPABASE_CONFIG.url
const supabaseAnonKey = SUPABASE_CONFIG.anonKey

// Debug logging
console.log('=== Supabase Initialization ===')
console.log('Supabase URL:', supabaseUrl)
console.log('Supabase Key length:', supabaseAnonKey?.length)
console.log('Supabase Key prefix:', supabaseAnonKey?.substring(0, 20) + '...')

// Validate URL format
try {
  const url = new URL(supabaseUrl)
  console.log('✅ URL format is valid:', url.href)
} catch (e) {
  console.error('❌ Invalid URL format:', e)
}

// Create Supabase client with options
const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  },
  global: {
    headers: {
      'X-Client-Info': 'supabase-js-web'
    }
  }
})

// Test the client immediately
console.log('Supabase client created:', !!supabase)
console.log('Supabase auth:', !!supabase.auth)
console.log('Supabase storage:', !!supabase.storage)

export default boot(({ app }) => {
  // Make supabase available globally
  app.config.globalProperties.$supabase = supabase
  console.log('✅ Supabase client initialized successfully in boot')
  
  // Run a quick connection test
  setTimeout(async () => {
    try {
      console.log('Running initial connection test...')
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .limit(1)
      
      if (error) {
        console.error('❌ Initial connection test failed:', error)
      } else {
        console.log('✅ Initial connection test successful')
      }
    } catch (e) {
      console.error('❌ Initial connection test exception:', e)
    }
  }, 1000)
})

export { supabase }