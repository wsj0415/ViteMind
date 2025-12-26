import DefaultTheme from 'vitepress/theme'
import PayWall from './components/PayWall.vue'
import PricingSection from './components/PricingSection.vue'
import './style.css'

export default {
    extends: DefaultTheme,
    enhanceApp({ app }) {
        app.component('PayWall', PayWall)
        app.component('PricingSection', PricingSection)
    }
}
