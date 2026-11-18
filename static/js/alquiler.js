
(function () {
  "use strict";

  const formulario = document.getElementById("form-alquiler");
  if (!formulario) return;

  const cuerpo = document.getElementById("cuerpo-servicios");
  const plantilla = document.getElementById("plantilla-fila-servicio");
  const btnAgregar = document.getElementById("btn-agregar-servicio");

  const selCliente = document.getElementById("id_fk_cli_id");
  const selVehiculo = document.getElementById("id_fk_veh_id");
  const inpFecha = document.getElementById("id_alq_fecha_inicio");
  const inpDias = document.getElementById("id_dias");

  const ETIQUETAS = {
    tarifa: document.getElementById("etq-tarifa"),
    periodo: document.getElementById("etq-periodo"),
    subtotalServicios: document.getElementById("etq-subtotal-servicios"),
    smTarifa: document.getElementById("sm-tarifa"),
    smDias: document.getElementById("sm-dias"),
    smSubVehiculo: document.getElementById("sm-subtotal-vehiculo"),
    smSubServicios: document.getElementById("sm-subtotal-servicios"),
    smTotal: document.getElementById("sm-total"),
  };

  const formatoCOP = new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  });


  const manejo = formulario.querySelector("input[name$='-TOTAL_FORMS']");
  const prefijo = manejo ? manejo.name.slice(0, -"-TOTAL_FORMS".length) : "";

  let tarifas = {};  
  let precios = {};  

  function numero(valor) {
    const n = parseFloat(valor);
    return isNaN(n) ? 0 : n;
  }

  function filas() {
    return Array.from(cuerpo ? cuerpo.querySelectorAll("tr.fila-servicio") : []);
  }

  function filaMarcada(fila) {
    const borrar = fila.querySelector("input[type='checkbox'][name$='-DELETE']");
    return Boolean(borrar && borrar.checked);
  }

  function actualizarPreciosUnitarios() {
    filas().forEach(function (fila) {
      const select = fila.querySelector("select");
      const celda = fila.querySelector(".precio");
      if (!select || !celda) return;
      const precio = precios[select.value];
      celda.textContent = precio ? formatoCOP.format(numero(precio)) : "—";
    });
  }

  function recalcular() {
    const vehiculo = selVehiculo ? selVehiculo.value : "";
    const tarifa = numero(tarifas[vehiculo]);
    const dias = inpDias ? Math.max(0, parseInt(inpDias.value || "0", 10) || 0) : 0;

    let subtotalServicios = 0;
    filas().forEach(function (fila) {
      const select = fila.querySelector("select");
      const cantidad = fila.querySelector("input[type='number']");
      const celda = fila.querySelector(".importe");
      if (!select || !cantidad || !celda) return;

      const precio = numero(precios[select.value]);
      const unidades = filaMarcada(fila) ? 0 : Math.max(0, parseInt(cantidad.value || "0", 10) || 0);
      const importe = select.value ? precio * unidades : 0;
      celda.textContent = select.value ? formatoCOP.format(importe) : "—";
      subtotalServicios += importe;
    });

    const subtotalVehiculo = tarifa * dias;
    const total = subtotalVehiculo + subtotalServicios;

    if (ETIQUETAS.tarifa) ETIQUETAS.tarifa.textContent = tarifa ? formatoCOP.format(tarifa) : "—";
    if (ETIQUETAS.periodo) ETIQUETAS.periodo.textContent = textoPeriodo(dias);
    if (ETIQUETAS.subtotalServicios) ETIQUETAS.subtotalServicios.textContent = formatoCOP.format(subtotalServicios);
    if (ETIQUETAS.smTarifa) ETIQUETAS.smTarifa.textContent = tarifa ? formatoCOP.format(tarifa) : "—";
    if (ETIQUETAS.smDias) ETIQUETAS.smDias.textContent = String(dias);
    if (ETIQUETAS.smSubVehiculo) ETIQUETAS.smSubVehiculo.textContent = formatoCOP.format(subtotalVehiculo);
    if (ETIQUETAS.smSubServicios) ETIQUETAS.smSubServicios.textContent = formatoCOP.format(subtotalServicios);
    if (ETIQUETAS.smTotal) ETIQUETAS.smTotal.textContent = formatoCOP.format(total);
  }

  function textoPeriodo(dias) {
    if (!inpFecha || !inpFecha.value) return "—";
    const inicio = new Date(inpFecha.value + "T12:00:00");
    if (isNaN(inicio.getTime())) return "—";
    if (!dias) return inicio.toLocaleDateString("es-CO");
    const fin = new Date(inicio.getTime());
    fin.setDate(fin.getDate() + dias);
    return (
      inicio.toLocaleDateString("es-CO") + "  →  " + fin.toLocaleDateString("es-CO")
    );
  }

  function agregarFila() {
    if (!plantilla || !manejo) return;
    const indice = parseInt(manejo.value, 10) || 0;
    const contenedor = document.createElement("tbody");
    contenedor.innerHTML = plantilla.innerHTML.replace(/__prefix__/g, String(indice));
    const nueva = contenedor.firstElementChild;
    if (!nueva) return;
    cuerpo.appendChild(nueva);
    manejo.value = String(indice + 1);
    recalcular();
    const select = nueva.querySelector("select");
    if (select) select.focus();
  }

  // eventos
  [selVehiculo, inpFecha, inpDias].forEach(function (campo) {
    if (!campo) return;
    campo.addEventListener("change", recalcular);
    campo.addEventListener("input", recalcular);
  });

  if (cuerpo) {
    cuerpo.addEventListener("change", function (ev) {
      const fila = ev.target.closest("tr.fila-servicio");
      if (!fila) return;
      if (ev.target.matches("select")) {
        const celda = fila.querySelector(".precio");
        const precio = precios[ev.target.value];
        if (celda) celda.textContent = precio ? formatoCOP.format(numero(precio)) : "—";
      }
      recalcular();
    });
    cuerpo.addEventListener("input", recalcular);
  }

  if (btnAgregar) btnAgregar.addEventListener("click", agregarFila);
  if (selCliente) selCliente.addEventListener("change", recalcular);

  //  carga de tarifas y precios 
  const url = formulario.dataset.calculoUrl;
  if (url) {
    fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
      .then(function (datos) {
        Object.entries(datos.vehiculos || {}).forEach(function (par) {
          tarifas[par[0]] = par[1].tarifa;
        });
        Object.entries(datos.servicios || {}).forEach(function (par) {
          precios[par[0]] = par[1].precio;
        });
        actualizarPreciosUnitarios();
        recalcular();
      })
      .catch(function () {
        
      });
  }

  recalcular();
})();
