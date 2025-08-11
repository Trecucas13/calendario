# Documentación del Loader Global

## Descripción
El sistema de loader global está configurado para funcionar automáticamente en todos los roles y páginas de la aplicación.

## Funcionalidad Automática

### El loader se muestra automáticamente cuando:
- Se envía un formulario (submit)
- Se hace clic en un enlace de navegación
- Se abandona la página (beforeunload)
- Se ejecutan botones con `onclick` que contienen navegación

### El loader NO se muestra cuando:
- El enlace tiene `href="#"` o `href="javascript:"`
- El enlace tiene `target="_blank"`
- El elemento tiene el atributo `data-no-loader`
- El formulario tiene el atributo `data-no-loader`

## Uso Manual

### Funciones Globales Disponibles:
```javascript
// Mostrar loader manualmente
window.showGlobalLoader();

// Ocultar loader manualmente  
window.hideGlobalLoader();
```

### Utilidades Adicionales:
```javascript
// Para descargas de archivos
window.loaderUtils.showForDownload(buttonElement);

// Para peticiones AJAX
window.loaderUtils.showForAjax();
window.loaderUtils.hideForAjax();

// Para elementos específicos
window.loaderUtils.addToElement(element);
window.loaderUtils.removeFromElement(element);

// Para formularios con confirmación
window.loaderUtils.submitFormWithLoader(formElement, "¿Está seguro?");
```

## Prevenir el Loader

### Para enlaces:
```html
<a href="/ruta" data-no-loader>Enlace sin loader</a>
```

### Para formularios:
```html
<form method="post" data-no-loader>
    <!-- Contenido del formulario -->
</form>
```

### Para botones:
```html
<button onclick="miFuncion()" data-no-loader>Botón sin loader</button>
```

## Archivos Involucrados

- **CSS**: `/static/css/loader.css`
- **JavaScript**: `/static/js/loader-utils.js`
- **Template Base**: `/templates/base.html`

## Notas Importantes

1. El loader está configurado con z-index alto (99999) para aparecer sobre todo el contenido
2. Se incluye backdrop-filter para mejor efecto visual
3. Compatible con Bootstrap modals
4. Funciona en todos los roles sin configuración adicional
5. Los loaders duplicados en templates específicos han sido removidos

## Troubleshooting

Si el loader no aparece:
1. Verificar que el elemento no tenga `data-no-loader`
2. Asegurar que JavaScript esté habilitado
3. Verificar la consola del navegador por errores
4. Confirmar que `/static/css/loader.css` se esté cargando correctamente
