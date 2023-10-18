import React, { FC } from 'react';
import './index.scss';

interface IFooter{}


const Footer:FC<IFooter>=()=>{
    return (
      <div className='footer' data-testid='footer'>
          {/* Made with <img className='heart' src='/static/images/heart-icon.png'/> by&nbsp; 
          <a href='https://kartoza.com' target='_blank' style={{ color: "var(--white)"}}>Kartoza</a> */}
            <div className='sanbi-footer-logo-container'>
                <img className='footer-logo' data-testid='sanbi-footer-logo'
                src='/static/images/footer/sanbi-footer-logo.png'/>
            </div>
            <div className='footer-nav' data-testid='footer-navigation'>
                <a href='/' target='_blank'>HOME</a>
                <a href='/map' target='_blank'>EXPLORE</a>
                <a href='/' target='_blank'>DOCUMENTATION</a>
                <a href='/contact' target='_blank'>CONTACT</a>
          </div>
          <div className='vendors-logos-container' data-testid='vendors-logos-container'>
            <img className='ids-logo' src='/static/images/footer/ids-logo.png' data-testid='ids-logo'/>
            <img className='kartoza-white-logo' src='/static/images/footer/kartoza-white-logo.png' data-testid='kartoza-logo'/>
          </div>
      </div>
    );
  }


  export default Footer