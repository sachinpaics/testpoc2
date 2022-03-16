from xmlrpc.server import list_public_methods
import pdftotree
from bs4 import BeautifulSoup
import datetime
import nltk
# nltk.download('punkt')

import json
import difflib as dl

import threading
from threading import Thread
from   multiprocessing.pool import ThreadPool
import asyncio

async def main():

    T_start_time = datetime.datetime.now()

    doc1paragraphs = []
    doc2paragraphs = []


    ##### Declaring the Path of the files.

    file_1 = "payLoad/Sample_5_doc1.pdf"
    file_2 = "payLoad/Sample_5_doc2.pdf"

    # file_1 = "payLoad/Sample_10_doc1.pdf"
    # file_2 = "payLoad/Sample_10_doc2.pdf"

    # file_1 = "payLoad/Sample_20_doc1.pdf"
    # file_2 = "payLoad/Sample_20_doc2.pdf"

    # file_1 = "payLoad/Doc1.pdf"
    # file_2 = "payLoad/Doc2.pdf"

    output_path = "outputFile/output_exp.json"

    await(file_reading(file_1, file_2, output_path, doc1paragraphs, doc2paragraphs))

    # parsing_html()



    T_end_time =  datetime.datetime.now()

    TIME_TAKEN = T_end_time - T_start_time
    print(TIME_TAKEN)


async def data_fetch_file1(soup1, doc1paragraphs):

    print("Inside HTML parsing doc 1")


    word_list = []
    for t in soup1.findAll():
        if "class" in t.attrs.keys() and "title" in t.attrs.keys():
            word_list.append(t.text)
        elif "title" in t.attrs.keys() and "class" not in t.attrs.keys():
            word_list.append("Image Found")
    s_out = (" ".join(word_list))
    s_out = s_out.replace("\n"," ")
    corrections = []
    all_sentences = nltk.sent_tokenize(s_out)
    for each_sentence in all_sentences:
        corrections.append(each_sentence)

    # doc1paragraphs = []
    for sent in corrections:
        all = nltk.word_tokenize(sent)
        if all[0]==all[1]:
            all.pop(0)
            all[0:2] = [''.join(all[0:2])]
            doc1paragraphs.append(' '.join(all))
        else:
            doc1paragraphs.append(sent)     

    return doc1paragraphs                  


async def data_fetch_file2(soup2, doc2paragraphs):

    print("Inside HTML parsing doc 2")

    start_time = datetime.datetime.now()

    word_list = []
    for t in soup2.findAll():
        if "class" in t.attrs.keys() and "title" in t.attrs.keys():
            word_list.append(t.text)
        elif "title" in t.attrs.keys() and "class" not in t.attrs.keys():
            word_list.append("Image Found")
    s_out = (" ".join(word_list))
    s_out = s_out.replace("\n"," ")
    corrections = []
    all_sentences = nltk.sent_tokenize(s_out)
    for each_sentence in all_sentences:
        corrections.append(each_sentence)

    # doc2paragraphs = []
    for sent in corrections:
        all = nltk.word_tokenize(sent)
        if all[0]==all[1]:
            all.pop(0)
            all[0:2] = [''.join(all[0:2])]
            doc2paragraphs.append(' '.join(all))
        else:
            doc2paragraphs.append(sent)
    

    return doc2paragraphs            

async def processFile(file):
    xmlText = pdftotree.parse(file, html_path=None, model_type=None, model_path=None, visualize=True)
    soup = BeautifulSoup(xmlText,'html.parser')
    return soup

async def file_reading(file_1, file_2, output_path, doc1paragraphs, doc2paragraphs):

    print("In File Reading")

    start_time = datetime.datetime.now()

    soup1 = await(processFile(file_1))
    soup2 = await(processFile(file_2))
    end_time = datetime.datetime.now()    

    time_taken = end_time - start_time

    print("Time taken to read both the files : ", time_taken)

    ########## Using Multi Threading code Starts ###################

    # print("Using Multi Threrading")

    # start_time = datetime.datetime.now()

    # doc1paragraphs = []
    # doc2paragraphs = []
 
    # t1 = threading.Thread(target = data_fetch_file1, args = (soup1, doc1paragraphs))
    # t2 = threading.Thread(target = data_fetch_file2, args = (soup2, doc2paragraphs))

    # t1.daemon = True
    # t2.daemon = True

    # t1.start()
    # t2.start()

    # t1.join()
    # t2.join()

    # end_time = datetime.datetime.now()    
    # time_taken = end_time - start_time
    # print("Time taken for PDF Compare : ", time_taken)

    ########## Using Multi Threading Code Ends ###################

    print("Without using Multi Threading")
    start_time = datetime.datetime.now()

    doc1paragraphs = await( data_fetch_file1(soup1, doc1paragraphs))
    doc2paragraphs = await( data_fetch_file2(soup2, doc2paragraphs))


    end_time = datetime.datetime.now()    
    time_taken = end_time - start_time
    print("Time taken for PDF Compare : ", time_taken)

    start_time = datetime.datetime.now()

    await pdf_compare(doc1paragraphs, doc2paragraphs, output_path)

    end_time = datetime.datetime.now()    

    time_taken = end_time - start_time

    print("Time taken for PDF Compare : ", time_taken)

async def pdf_compare(doc1paragraphs, doc2paragraphs, output_path):

    print("Inside PDF compare.")

    start_time = datetime.datetime.now()

    list_1 = doc1paragraphs
    list_2 = doc2paragraphs
    json_output = {"Doc1":[],"Doc2":[]}
    nearText = []
    for i in list_1:
        if i in list_2:
            json_output["Doc1"].append(f"<br> {i} </br>")
        else:
            nearText = dl.get_close_matches(i,list_2)
        if nearText:
            sentence1 = nltk.word_tokenize(i)
            sentence2 = nltk.word_tokenize(nearText[0])
            textC = []
            for word in sentence1:
                if word not in sentence2:
                    text = f"<mark> <b>{word}</b> </mark>"
                    textC.append(text)
                else:
                    textC.append(word)

            json_output["Doc1"].append("{} {} {}".format("<br>",' '.join(textC),"</br>"))
        else:
            text = f"<br> <mark> <b> {i} </b> </mark> </br>"
            json_output["Doc1"].append(text)
        
    # print("done1")
    for i in list_2:
        if i in list_1:
            json_output["Doc2"].append(f"<br> {i} </br>")
        else:
            nearText = dl.get_close_matches(i,list_1)
            if nearText:
                sentence1 = nltk.word_tokenize(i)
                sentence2 = nltk.word_tokenize(nearText[0])
                textC = []
                for word in sentence1:
                    if word not in sentence2:
                        text = f"<mark> <b>{word}</b> </mark>"
                        textC.append(text)
                    else:
                        textC.append(word)
                json_output["Doc2"].append("{} {} {}".format("<br>",' '.join(textC),"</br>"))
            else:
                text = f"<br> <mark> <b>{i}</b> </mark> </br>"
                json_output["Doc2"].append(text)

    # print("done2")

    send = {"Doc1":[],"Doc2":[]}

    send["Doc1"].append(str(' '.join(json_output["Doc1"])))
    send["Doc2"].append(str(' '.join(json_output["Doc2"])))


    with open(output_path, 'w', encoding='utf8') as json_file:
        json.dump(send, json_file, ensure_ascii=False)


            


if __name__ == "__main__" :
    asyncio.run(main() )   