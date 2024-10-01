import React, { Component } from "react";
import "./Books.css";
import { Fade } from "react-reveal";
import { books } from "../../portfolio";
import BookCard from "../../components/bookCard/BookCard";

class Books extends Component {
  render() {
    const theme = this.props.theme;
    return (
      <div className="main" id="certs">
        <div className="books-header-div">
          <Fade bottom duration={2000} distance="20px">
            <h1 className="books-header" style={{ color: theme.text }}>
              Bücher
            </h1>
          </Fade>
        </div>
        <div className="books-body-div">
          {books.books.map((book) => {
            return <BookCard book={book} theme={theme} />;
          })}
        </div>
      </div>
    );
  }
}

export default Books;
