from lxml import etree

seen_urls = set()

def process_xml_content(xml: str, archive_title: str) -> list[str]:
    """
    Process XML content, returning a list of contextualized strings.
    URLs which have already been processed are ignored.
    The returned strings are formatted as follows:

    FROM: {archive_title} - {doc_title} - {section}\\nCONTENT: {content}

    Content is extracted from text elements until the next 'head' tag.
    Prose formatting is stripped, lists and tables are converted to Markdown.
    """

    root: etree._Element = etree.fromstring(xml)

    # If we've already seen this URL, don't process.
    url = root.get("url")
    if url is not None:
        if url in seen_urls:
            return []
        seen_urls.add(url)

    doc_title = root.get("title")
    formatted_strings: list[str] = []
    heads: list[etree._Element] = root.xpath('.//main//head') # type: ignore
    
    # Traverse the XML to find <head> tags and extract text until the next <head>
    for head in heads:
        if head.text:
            section = head.text.strip()

        content_parts = []
        
        # Start collecting content after this head until the next head
        for sibling in head.itersiblings():
            if sibling.tag == 'head':
                break
            if sibling.tag in ['p', 'span']:
                content_parts.append(''.join(sibling.itertext()).strip()) # type: ignore
            elif sibling.tag == 'list':
                # Convert list to Markdown
                list_type = sibling.get("rend", "ul")
                items = sibling.findall('.//item')
                if list_type == "ul":
                    list_content = '\n'.join(f"- {item.text.strip()}" if item.text else "" for item in items)
                else:
                    list_content = '\n'.join(f"{index + 1}. {item.text.strip()}" if item.text else "" for index, item in enumerate(items))
                content_parts.append(list_content)
            elif sibling.tag == 'table':
                # Convert table to markdown
                headers = [th.text.strip() for th in sibling.xpath('.//th')] # type: ignore
                rows = [
                    '|' + '|'.join([td.text.strip() for td in tr.findall('.//td')]) + '|' # type: ignore
                    for tr in sibling.findall('.//tr')
                ]
                header_row = '|' + '|'.join(headers) + '|'
                separator = '|' + '|'.join(['---'] * len(headers)) + '|'
                table_content = '\n'.join([header_row, separator] + rows)
                content_parts.append(table_content)
        
        # Format and append the string
        string_parts = [part for part in [archive_title, doc_title, section] if part]
        formatted_string = "FROM: " + " - ".join(string_parts) + "\nCONTENT: " + " ".join(content_parts)
        formatted_strings.append(formatted_string)
    
    return formatted_strings