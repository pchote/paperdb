function buildnames(data, type, row, meta) {
  // Only display the first author, but include all authors so they can be indexed in the search field
  if (data instanceof Array)
    return data[0] + (data.length > 1 ? ' et. al.' : '') + '<span style="display: none">' + data.join(' ') + '</span>';
  return data;
}

function buildtitle(data, type, row, meta) {
  // Include the abstract and keywords so they can be indexed by the search field
  return data + '<span style="display: none">' + row['abstract'] + row['keywords'] + '</span>';
}

function bind_paper_button(button, url) {
  if (url) {
    button.attr('href', url);
    button.show();
  } else
    button.hide();
}

function setup(data_url) {
  var table = $('#table').DataTable( {
    ajax: { url: data_url, dataSrc: '' },
    dom: "<'row'<'col-sm-6'f><'col-sm-6'p>><'row'<'col-sm-12'tr>><'row'<'col-sm-6'l><'col-sm-6'p>>",
    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
    columns: [
      { data: 'author', width: '17%', render: buildnames },
      { data: 'year', width: '8%' },
      { data: 'title', width: '50%', render: buildtitle },
      { data: 'journal', width: '25%' },
    ]
  });

  $('#table tbody').on('click', 'tr', function () {
    var element = table.row( this ).data();

    $('#detailmodal').modal();
    $('#paper-title').text(element.title);
    $('#paper-author').html(element.author.join(' and '));
    $('#paper-journal').html(element.journal);
    $('#paper-year').html(element.year);
    $('#paper-abstract').text(element.abstract);
    $('#paper-bibtex').text(element.bib);
    $('.nav-tabs a:first').tab('show');

    if (element.keywords) {
      $('#paper-keywords').html(element.keywords.split(',').join('<br />'));
      $('#keywords-tab').show();
    } else
      $('#keywords-tab').hide();

    bind_paper_button($('#paper-pdf'), element.pdf);
    bind_paper_button($('#paper-ads'), element.ads);
    bind_paper_button($('#paper-doi'), element.doi);
    bind_paper_button($('#paper-arxiv'), element.arxiv);
    bind_paper_button($('#paper-web'), element.web);
  });
}
