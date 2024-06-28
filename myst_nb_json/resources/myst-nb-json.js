// Script to be embedded inside the component's root HTMLElement
(function (component) {
    document.addEventListener('DOMContentLoaded', () => {
        const CLASS_KEY = "myst-nb-json-key";
        const CLASS_COLLAPSIBLE = "myst-nb-json-collapsible";
        const CLASS_COLLAPSED = "myst-nb-json-collapsed";

        let toggleable = Array.from(component.getElementsByTagName("li"));
        toggleable.forEach((li) => {
            // Find list item elements that contain a nested, collapsible value.
            if (li.getElementsByClassName(CLASS_COLLAPSIBLE).length == 0) return;
            let key = li.getElementsByClassName(CLASS_KEY)[0];
            let toggleFn = function() {
                let isCollapsed = li.classList.contains(CLASS_COLLAPSED);
                if (isCollapsed) {
                    li.classList.remove(CLASS_COLLAPSED);
                } else {
                    li.classList.add(CLASS_COLLAPSED);
                }
            }
            // Make the key element interactive to toggle the list item's collapsed state.
            key.addEventListener("click", toggleFn);
            key.addEventListener("keydown", (event) => {
                if (event.code === "ArrowLeft" || event.code === "ArrowRight" || event.code === "Space") toggleFn()
            });
        });
    });
})(document.currentScript.parentElement);
