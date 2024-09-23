import React, { Component } from "react";
import "./BookCard.css";
import { Fade } from "react-reveal";

class BookCard extends Component {
  render() {
    const book = this.props.book;
    const theme = this.props.theme;
    return (
      <Fade bottom duration={2000} distance="20px">
        <div className="cert-card">
          <div className="content">
            <a href={book.book_link} target="_blank" rel="noopener noreferrer">
              <div className="content-overlay"></div>
              <div
                className="cert-header"
                style={{ backgroundColor: book.color_code }}
              >
                <img
                  className="logo_img"
                  src={require(`../../assets/images/${book.logo_path}`)}
                  alt={book.alt_name}
                />
              </div>
              <div className="content-details fadeIn-top">
                <h3 className="content-title" style={{ color: theme.body }}>
                  Amazon Link
                </h3>
              </div>
            </a>
          </div>
          <div className="cert-body">
            <h2 className="cert-body-title" style={{ color: theme.text }}>
              {book.title}
            </h2>
            <h3
              className="cert-body-subtitle"
              style={{ color: theme.secondaryText }}
            >
              {book.subtitle}
            </h3>
          </div>
        </div>
      </Fade>
    );
  }
}

export default BookCard;
