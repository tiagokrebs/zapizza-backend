"use strict";
/* base: https://datatables.net/manual/i18n
*/
    $(document).on('ready', function() {
                $('#dataTables-simple').DataTable({
                        responsive: true,
                        pageLength:50,
                        "lengthMenu": [ 50, 100, 200 ],
                        sPaginationType: "full_numbers",
                        oLanguage: {
                            "sEmptyTable": "Nenhum registro encontrado",
                            "sInfo": "_TOTAL_ registros (_START_ até _END_)",
                            "sInfoEmpty": "Nenhum registro encontrado",
                            "sInfoFiltered": " - filtrados de _MAX_ registros",
                            "sInfoThousands": ".",
                            "sLengthMenu": "Exibir _MENU_ registros",
                            "sLoadingRecords": "Carregando...",
                            "sProcessing": "Processando...",
                            "sSearch": "Pesquisar",
                            "sZeroRecords": "Nenhum registro encontrado",
                            oPaginate: {
                                sFirst: "<<",
                                sPrevious: "<",
                                sNext: ">",
                                sLast: ">>"
                            }
                        }
                    });
            });