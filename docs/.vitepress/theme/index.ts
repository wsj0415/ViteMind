import DefaultTheme from 'vitepress/theme'
import PayWall from './components/PayWall.vue'
import PricingSection from './components/PricingSection.vue'
import NewsGallery from './components/NewsGallery.vue'
import AiToolsGallery from './components/AiToolsGallery.vue'
import NewsletterForm from './components/NewsletterForm.vue'
import HomeBanner from './components/HomeBanner.vue'
import DesignResourcesGallery from './components/DesignResourcesGallery.vue'
import AdminLogin from './components/admin/AdminLogin.vue'
import AdminLayout from './components/admin/AdminLayout.vue'
import AdminDashboard from './components/admin/AdminDashboard.vue'
import DataManager from './components/admin/DataManager.vue'
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
        app.component('AdminLogin', AdminLogin)
        app.component('AdminLayout', AdminLayout)
        app.component('AdminDashboard', AdminDashboard)
        app.component('DataManager', DataManager)
    }
}
