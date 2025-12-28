import DefaultTheme from 'vitepress/theme'
import PayWall from './components/PayWall.vue'
import PricingSection from './components/PricingSection.vue'
import NewsGallery from './components/NewsGallery.vue'
import AiToolsGallery from './components/AiToolsGallery.vue'
import NewsletterForm from './components/NewsletterForm.vue'
import HomeBanner from './components/HomeBanner.vue'
import DesignResourcesGallery from './components/DesignResourcesGallery.vue'
import './style.css'

export default {
    extends: DefaultTheme,
    enhanceApp({ app }) {
        app.component('PayWall', PayWall)
        app.component('PricingSection', PricingSection)
        app.component('NewsGallery', NewsGallery)
        app.component('AiToolsGallery', AiToolsGallery)
        app.component('NewsletterForm', NewsletterForm)
        app.component('HomeBanner', HomeBanner)
        app.component('DesignResourcesGallery', DesignResourcesGallery)
    }
}
