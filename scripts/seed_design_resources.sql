-- Initial data for design_resources table

INSERT INTO public.design_resources (title, description, url, category, tags, logo_url, is_featured, source) VALUES
-- Design Tools
('Figma', 'The leading collaborative interface design tool.', 'https://www.figma.com', 'Design Tools', ARRAY['Free', 'Premium', 'Web'], 'https://upload.wikimedia.org/wikipedia/commons/3/33/Figma-logo.svg', true, 'Official'),
('Sketch', 'The digital design toolkit for Mac.', 'https://www.sketch.com', 'Design Tools', ARRAY['Paid', 'Mac'], 'https://upload.wikimedia.org/wikipedia/commons/5/59/Sketch_Logo.svg', false, 'Official'),
('Adobe XD', 'Fast & powerful UI/UX design solution.', 'https://helpx.adobe.com/support/xd.html', 'Design Tools', ARRAY['Free', 'Premium'], 'https://upload.wikimedia.org/wikipedia/commons/c/c2/Adobe_XD_CC_icon.svg', false, 'Official'),

-- UI Libraries
('Material UI', 'MUI provides a robust, customizable, and accessible library of foundational and advanced components.', 'https://mui.com/', 'UI Libraries', ARRAY['React', 'Free', 'Open Source'], 'https://mui.com/static/logo.png', true, 'Official'),
('Ant Design', 'An enterprise-class UI design language and React UI library.', 'https://ant.design/', 'UI Libraries', ARRAY['React', 'Free', 'Open Source'], 'https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg', true, 'Official'),
('Tailwind CSS', 'A utility-first CSS framework for rapidly building custom designs.', 'https://tailwindcss.com/', 'UI Libraries', ARRAY['CSS', 'Free', 'Open Source'], 'https://upload.wikimedia.org/wikipedia/commons/d/d5/Tailwind_CSS_Logo.svg', true, 'Official'),
('Shadcn UI', 'Beautifully designed components that you can copy and paste into your apps.', 'https://ui.shadcn.com/', 'UI Libraries', ARRAY['React', 'Free', 'Open Source'], 'https://ui.shadcn.com/favicon.ico', true, 'Official'),

-- Icons & Fonts
('Font Awesome', 'The internet''s icon library and toolkit.', 'https://fontawesome.com/', 'Icons & Fonts', ARRAY['Icons', 'Free', 'Premium'], 'https://upload.wikimedia.org/wikipedia/commons/3/39/Font_Awesome_logo.png', false, 'Official'),
('Google Fonts', 'Making the web more beautiful, fast, and open through great typography.', 'https://fonts.google.com/', 'Icons & Fonts', ARRAY['Fonts', 'Free'], 'https://upload.wikimedia.org/wikipedia/commons/e/ee/Google_Fonts_logo.svg', true, 'Official'),
('Lucide', 'Beautiful & consistent icon toolkit made by the community.', 'https://lucide.dev/', 'Icons & Fonts', ARRAY['Icons', 'Free', 'Open Source'], 'https://lucide.dev/logo.svg', true, 'Official'),

-- Colors
('Coolors', 'The super fast color palettes generator!', 'https://coolors.co/', 'Colors', ARRAY['Generator', 'Free'], 'https://coolors.co/assets/img/logo.svg', true, 'Official'),
('Adobe Color', 'Create color palettes with the color wheel or image, browse thousands of color combinations.', 'https://color.adobe.com/', 'Colors', ARRAY['Generator', 'Free'], 'https://color.adobe.com/favicon.ico', false, 'Official'),

-- Design Systems
('Material Design', 'Build beautiful, usable products faster.', 'https://m3.material.io/', 'Design Systems', ARRAY['Google', 'Guide'], 'https://upload.wikimedia.org/wikipedia/commons/c/c7/Google_Material_Design_Logo.svg', true, 'Official'),
('Human Interface Guidelines', 'Best practices for creating great experiences on Apple platforms.', 'https://developer.apple.com/design/human-interface-guidelines/', 'Design Systems', ARRAY['Apple', 'Guide'], 'https://developer.apple.com/favicon.ico', true, 'Official'),

-- Learning
('Refactoring UI', 'Learn how to design beautiful user interfaces by yourself using specific tactics explained from a developer''s point-of-view.', 'https://www.refactoringui.com/', 'Learning', ARRAY['Book', 'Paid'], 'https://www.refactoringui.com/favicon.ico', true, 'Official'),
('Laws of UX', 'A collection of best practices that designers can consider when building user interfaces.', 'https://lawsofux.com/', 'Learning', ARRAY['Guide', 'Free'], 'https://lawsofux.com/favicon.ico', false, 'Official'),

-- Inspiration
('Dribbble', 'Discover the world’s top designers & creative professionals.', 'https://dribbble.com/', 'Inspiration', ARRAY['Gallery', 'Free'], 'https://upload.wikimedia.org/wikipedia/commons/3/32/Dribbble_logo.svg', true, 'Official'),
('Behance', 'Showcase and discover creative work.', 'https://www.behance.net/', 'Inspiration', ARRAY['Gallery', 'Free'], 'https://upload.wikimedia.org/wikipedia/commons/c/c5/Behance_logo.svg', false, 'Official'),
('Awwwards', 'The awards that recognize the talent and effort of the best web designers, developers and agencies in the world.', 'https://www.awwwards.com/', 'Inspiration', ARRAY['Gallery', 'Awards'], 'https://assets.awwwards.com/assets/images/logo-awwwards-white.svg', false, 'Official'),

-- Prototyping
('Framer', 'Design and publish your dream site.', 'https://www.framer.com/', 'Prototyping', ARRAY['Web', 'No-Code'], 'https://www.framer.com/images/favicons/favicon.png', true, 'Official'),
('ProtoPie', 'The easiest tool to turn your UI/UX design ideas into highly interactive prototypes.', 'https://www.protopie.io/', 'Prototyping', ARRAY['Interaction', 'Paid'], 'https://www.protopie.io/favicon.ico', false, 'Official');

-- Phosphor Icons
INSERT INTO public.design_resources (title, description, url, category, tags, logo_url, is_featured, source) VALUES
('Phosphor Icons', 'A flexible icon family for interfaces, diagrams, presentations, and whatever else.', 'https://phosphoricons.com', 'Icons & Fonts', ARRAY['Icons', 'Free', 'Open Source', 'React', 'Vue'], 'https://phosphoricons.com/favicon.ico', true, 'Official');
