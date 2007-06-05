var Paginator =
{
    jumpToPage: function(pages, query)
    {
        var page = prompt("Enter a number between 1 and " + pages + " to jump to that page", "");
        if (page != undefined)
        {
            page = parseInt(page, 10)
            if (!isNaN(page) && page > 0 && page <= pages)
            {
              if (query != "") {
                window.location.href = "?page=" + page + "&" +  query;
              } else {
                window.location.href = "?page=" + page;
              }
            }
        }
    }
};
