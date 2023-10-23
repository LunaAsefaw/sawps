import React, {FC} from 'react';
import './index.scss';

import {DocsCrawlerPage} from "django-docs-crawler-react";

import "django-docs-crawler-react/dist/style.css"

interface IHelp {
}

const Help: FC<IHelp> = () => {
    return (
        <>
            <div className='help-container' data-testid='help-container'>
                <div className='help-content-container'>
                    <div className='help-image-container'>
                        <img src='/static/images/help/help_page_banner.png'
                             className="help-banner-img" alt="Help Banner"/>
                    </div>
                    <div className='help-texts-container'>
                        <DocsCrawlerPage
                            dataUrl={'/docs_crawler/data'}
                            open={true}
                            setOpen={() => {
                            }}
                            footer={
                                <div className='help-btns-container'>
                                    <a href="/contact">
                                        <button
                                            className="orange-button sawps-font-button-black">
                                            Contact us
                                        </button>
                                    </a>
                                </div>
                            }
                        />
                    </div>
                </div>
            </div>
        </>
    )
}

export default Help