import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { Error.interceptor } from './error.interceptor';

describe('Error.interceptor', () => {
  let component: Error.interceptor;
  let fixture: ComponentFixture<Error.interceptor>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        Error.interceptor,
        HttpClientTestingModule
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Error.interceptor);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
