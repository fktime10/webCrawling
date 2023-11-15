# -*- coding: utf-8 -*-

import argparse
import asyncio
import datetime
import logging
import os
import scrapy
import sys
from scrapy.crawler import CrawlerRunner
from scrapy.shell import inspect_response
from tldextract import extract       ### !!nur in DEV!!
from twisted.internet import reactor
from spiders import bb, be, bund, bw, by, hb, hh, he, mv, ni, nw, rp, sh, sl, sn, st, th
from src import config
from src.output import output

from scrapy.utils.project import get_project_settings


async def run_crawler(crawler_runner, spider_class, **kwargs):
    try:
        settings = get_project_settings()
        runner = CrawlerRunner(settings)
        await runner.crawl(spider_class, **kwargs)
    except Exception as e:
        output(f"Error running crawler: {e}", "err")


async def main():
    output("Due to the terms of use governing the databases accessed by gesp, the use of gesp is only permitted for non-commercial purposes. Do you use gesp exclusively for non-commercial purposes?")
    inp = input("[Y]es/[N]o: ")
    try:
        inp = inp.lower()
    except:
        sys.exit()
    else:
        if inp != "y" and inp != "yes":
            sys.exit()
    cl_courts, cl_states, cl_domains = [], [], []
    cl_parser = argparse.ArgumentParser(prog="gesp", description="scraping of german court decisions")
    cl_parser.add_argument("-c", "--courts", type=str.lower, help="individual selection of the included courts (ag/lg/olg/...)")
    cl_parser.add_argument("-d", "--domains", type=str.lower, help="individual selection of the included legal domains (oeff/zivil/straf)")
    cl_parser.add_argument("-p", "--path", type=str, help="sets the path where the results will be stored")
    cl_parser.add_argument("-s", "--states", type=str.lower, help="individual selection of the included states (bund/bb/be/bw/by/...)")
    cl_parser.add_argument("-v", "--version", action="version", version=f"gesp {config.__version__} by {config.__author__} (nwais.de)", help="version of this package")
    cl_parser.add_argument('--docId', action='store_true', help="appends the docId, if present, to the filename")
    cl_parser.add_argument("-fp", "--fingerprint", nargs="?", const=True, help="creates (flag) or reads (argument, path) a fingerprint file")
    cl_parser.add_argument("-pp", "--postprocess", action=argparse.BooleanOptionalAction, help="turns on postprocessing of the downloaded decisions, removing all html elements and transforming them into a more easily machine readable format")
    cl_parser.add_argument("-w", "--wait", action=argparse.BooleanOptionalAction, help="inserts a delay after downloading each decision, which can avoid a ban from the service providers (mainly juris)")
    args = cl_parser.parse_args()
    # -p (path)
    path = os.path.join(os.getcwd(), "results", datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
    if (args.path):
        if os.path.isdir(args.path):
            path = args.path
        else:
            output(f"creating new folder {args.path}...")
            try:
                os.makedirs(args.path)
            except:
                output(f"could not create folder {args.path}", "err")
            else:
                path = args.path
    else:
        n = 1
        while os.path.exists(path): # Für den Fall, dass der Standrad-Pfad durch einen früheren Durchgang belegt ist
            path = f"{path}_{n}"
            n += 1
        try:
            os.makedirs(path)
        except:
            output(f"could not create folder {path}", "err")
    #if path[-1] != "/": path = path + "/"
    # -c (courts)
    if (args.courts):
        for court in args.courts.split(","):
            if (not court in config.COURTS and court != "larbg" and court != "vgh"):
                output(f"unknown court '{court}'", "err")
            elif (court == "larbg"): # larbg = lag
                output(f"court '{court}' is interpreted as 'lag'", "warn")
                cl_courts.append("lag")
            elif (court == "vgh"): # vgh = ovg
                output(f"court '{court}' is interpreted as 'ovg'", "warn")
                cl_courts.append("lag")
            else:
                cl_courts.append(court)
    # -s (states)
    if (args.states):
        for state in args.states.split(","):
            if (not state in config.STATES):
                output(f"unknown state '{state}'", "err")
            else:
                cl_states.append(state)
    else:
        if cl_courts and set(cl_courts).issubset({"bgh", "bfh", "bverwg", "bverfg", "bpatg", "bag", "bsg"}):
            cl_states.append("bund") # Nur Bundesgericht(e) angegebeben, aber nicht auf Bund eingegrenzt ("-s bund"): Eingrenzung auf Bundesportal
        else:
            cl_states.extend(config.HTML_STATES)  # Sachsen und Bremen (PDF) nur bei expliziter Nennung
    # -d (domains)
    if (args.domains):
        for domain in args.domains.split(","):
            if (not domain in config.DOMAINS):
                output(f"unknown legal domain '{domain}'", "err")
            else:
                cl_domains.append(domain)
    # -pp (postprocess)
    if args.postprocess != True: args.postprocess = False
    # -w (wait)
    if args.wait != True: args.wait = False
    # -fp (fingerprint)
    if isinstance(args.fingerprint, str): # fp als Argument
        fp = args.fingerprint
        if not os.path.exists(fp):
            output(f"file {fp} does not exist", "err")
        elif not os.path.isfile(fp):
            output(f"file {fp} is a folder, not a file", "err")
        else:
            fp_importer = Fingerprint(path, fp, args.store_docId)
    else:  # fp als Flag / kein fp
        if args.fingerprint == True:
            fp = args.fingerprint
        else:
            fp = False
        logging.getLogger('scrapy').propagate = True
        logger = logging.getLogger('scrapy')
        logger.propagate = False
        logger.setLevel(logging.DEBUG)
        crawlers = [
            bund.SpdrBund, bw.SpdrBW, by.SpdrBY, be.SpdrBE, bb.SpdrBB,
            hb.SpdrHB, hh.SpdrHH, he.SpdrHE, mv.SpdrMV, ni.SpdrNI,
            nw.SpdrNW, rp.SpdrRP, sh.SpdrSH, sl.SpdrSL, sn.SpdrSN,
            st.SpdrST, th.SpdrTH
        ]
        crawlers_2 = [
            sh.SpdrSH

        ]

        tasks = []
        tasks = []
        for crawler_class in crawlers_2:
            if (cl_states and crawler_class.__name__.lower()[4:] not in cl_states):
                continue
            task = run_crawler(CrawlerRunner(), crawler_class, path=path, courts=cl_courts, states=cl_states, fp=fp,
                               domains=cl_domains, store_docId=args.docId, postprocess=args.postprocess, wait=args.wait)
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks)
            reactor.run(installSignalHandlers=False)

if __name__ == "__main__":
    asyncio.run(main())
