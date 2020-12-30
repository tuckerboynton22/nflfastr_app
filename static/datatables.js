$(document).ready( function () {
    var t = $('#table_id').DataTable( {
    "columnDefs": [ {
        "searchable": false,
        "orderable": false,
        "targets": 0,
    } ],
    dom: 'Bfrtip',
    buttons: [
        'copy', 'csv', 'excel', 'pdf', 'print'
    ],
    "pageLength": 50,
    "order": []
    } );
    t.on( 'order.dt search.dt', function () {
        t.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        } );
    } ).draw();
} );