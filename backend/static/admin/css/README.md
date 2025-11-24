# Admin Panel CSS Architecture

This directory contains the CSS files for the Zento-themed admin panel redesign.

## File Structure

```
css/
├── zento-theme.css      # Core theme with CSS custom properties, reset, and utilities
├── components.css       # Reusable UI components (buttons, cards, forms, badges)
├── dashboard.css        # Dashboard-specific styles (metrics, charts, activity)
├── responsive.css       # Media queries for tablet and mobile devices
└── custom_admin.css     # Legacy custom styles (kept for compatibility)
```

## Load Order

The CSS files are loaded in the following order in `templates/admin/base_site.html`:

1. **zento-theme.css** - Foundation (variables, reset, utilities)
2. **components.css** - Reusable components
3. **dashboard.css** - Dashboard-specific styles
4. **responsive.css** - Responsive breakpoints
5. **custom_admin.css** - Legacy overrides

## CSS Custom Properties

All design tokens are defined as CSS custom properties in `zento-theme.css`:

- **Colors**: Primary, secondary, neutral, semantic colors
- **Typography**: Font families, sizes, weights, line heights
- **Spacing**: 4px-based spacing scale
- **Shadows**: Elevation system
- **Transitions**: Animation durations
- **Z-index**: Layering system

## Usage Examples

### Using Design Tokens

```css
.my-component {
  color: var(--primary-600);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
}
```

### Using Utility Classes

```html
<div class="flex items-center gap-4 bg-white rounded-lg shadow-md">
  <span class="text-primary font-semibold">Hello</span>
</div>
```

### Using Component Classes

```html
<button class="btn btn-primary">Save Changes</button>
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
  </div>
  <div class="card-body">
    Card content goes here
  </div>
</div>
```

## Responsive Breakpoints

- **Desktop**: > 1024px (default)
- **Tablet**: 768px - 1023px
- **Mobile**: < 768px
- **Small Mobile**: < 480px

## Browser Support

- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile Safari: iOS 13+
- Chrome Mobile: Android 8+

## Customization

To customize the theme, modify the CSS custom properties in `zento-theme.css`:

```css
:root {
  --primary-600: #your-color;
  --font-primary: 'Your Font', sans-serif;
  --space-4: 1rem;
}
```

## Performance

- All CSS files are minified in production
- Total CSS size: ~50KB (unminified)
- No external dependencies except Google Fonts (Inter)
- Uses modern CSS features (Grid, Flexbox, Custom Properties)

## Accessibility

- WCAG AA compliant color contrast ratios
- Focus indicators on all interactive elements
- Reduced motion support via `prefers-reduced-motion`
- High contrast mode support via `prefers-contrast`
- Semantic HTML structure

## Future Enhancements

- Dark mode support
- Theme customization UI
- Additional component variants
- Animation library
