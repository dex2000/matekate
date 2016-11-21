(function (factory, window) {
  // define an AMD module that relies on 'leaflet'
  if (typeof define === 'function' && define.amd) {
      define(['leaflet'], factory);

  // define a Common JS module that relies on 'leaflet'
  } else if (typeof exports === 'object') {
      module.exports = factory(require('leaflet'));
  }

  // attach your plugin to the global 'L' variable
  if (typeof window !== 'undefined' && window.L) {
      window.L.YourPlugin = factory(L);
  }
}(function (L) {
  L.Control.Infobox = L.Control.extend({
    options: {
      position: 'topleft',
      icon: 'fa fa-info'
    },

    initialize: function (options) {
      L.Util.setOptions(this, options);
    },

    onAdd: function (map) {
      var container = L.DomUtil.create('div','leaflet-control-infobox leaflet-bar leaflet-control');
      this._link = L.DomUtil.create('a', 'leaflet-bar-part leaflet-bar-part-single', container);
      this._icon = L.DomUtil.create('span', this.options.icon, this._link);
      this._map = map;
      this._container = container;

      L.DomEvent.on(this._link, 'click',
        function() {
          this.div = document.getElementById("infobox");
          if (this.div.style.display == "" || this.div.style.display == "none") {
            this.div.style.display = "block";
          }
          else {
            this.div.style.display = "none";
          }
        }
        , this);
      return container;
    }
  });

  L.control.infobox = function (options) {
      return new L.Control.Infobox(options);
  };
}, window));

