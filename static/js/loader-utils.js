/**
 * Funciones auxiliares para el loader global
 * Este archivo proporciona funciones adicionales para manejar el loader en casos especiales
 */

// Función para mostrar loader durante descargas
function showLoaderForDownload(buttonElement) {
  if (buttonElement) {
    const originalContent = buttonElement.innerHTML;
    buttonElement.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Descargando...';
    buttonElement.disabled = true;
    
    // Restaurar contenido después de 3 segundos (tiempo estimado de descarga)
    setTimeout(() => {
      buttonElement.innerHTML = originalContent;
      buttonElement.disabled = false;
    }, 3000);
  }
}

// Función para mostrar loader en formularios AJAX
function showLoaderForAjax() {
  if (typeof showGlobalLoader === 'function') {
    showGlobalLoader();
  }
}

// Función para ocultar loader después de AJAX
function hideLoaderForAjax() {
  if (typeof hideGlobalLoader === 'function') {
    hideGlobalLoader();
  }
}

// Función para agregar loader a un elemento específico
function addLoaderToElement(element) {
  if (element) {
    element.classList.add('loader-overlay', 'loading');
  }
}

// Función para remover loader de un elemento específico
function removeLoaderFromElement(element) {
  if (element) {
    element.classList.remove('loader-overlay', 'loading');
  }
}

// Función para manejar formularios con confirmación
function submitFormWithLoader(formElement, confirmMessage = null) {
  if (confirmMessage && !confirm(confirmMessage)) {
    return false;
  }
  
  if (typeof showGlobalLoader === 'function') {
    showGlobalLoader();
  }
  
  if (formElement) {
    formElement.submit();
  }
  
  return true;
}

// Exportar funciones para uso global
window.loaderUtils = {
  showForDownload: showLoaderForDownload,
  showForAjax: showLoaderForAjax,
  hideForAjax: hideLoaderForAjax,
  addToElement: addLoaderToElement,
  removeFromElement: removeLoaderFromElement,
  submitFormWithLoader: submitFormWithLoader
};
