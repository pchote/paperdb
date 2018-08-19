function buildnames(value, row, index) {
  // Only display the first author, but include all authors so they can be indexed in the search field
  if (value instanceof Array)
    return value[0] + (value.length > 1 ? ' et. al.' : '') + '<span style="display: none">' + value.join(' ') + '</span>';
  return value;
}

function buildtitle(value, row, index) {
  // Include the abstract and keywords so they can be indexed by the search field
  return value + '<span style="display: none">' + row['abstract'] + row['keywords'] + '</span>';
}

function bind_paper_button(button, url) {
  if (url) {
    button.attr('href', url);
    button.show();
  } else
    button.hide();
}

$(function() {
  $('#table').on('click-row.bs.table', function(row, element, field) {
    $('#detailmodal').modal();
    $('#paper-title').text(element.title);
    $('#paper-author').html(element.author);
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

  $('#table').on('load-error.bs.table', function() {
    $('#table').bootstrapTable('updateFormatText', 'NoMatches', 'There are no papers to display. Have you logged in?');
  });
});
