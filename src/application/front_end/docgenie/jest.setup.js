import '@testing-library/jest-dom'
import { TextEncoder, TextDecoder } from 'util'

// jsdom has neither, the chat page decodes the streamed response with them
Object.assign(global, { TextEncoder, TextDecoder })
